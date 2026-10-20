"""Pinned Unsloth MLX inference, isolated from the portable HTTP contract."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import tempfile


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify_files(pin, base, adapter):
    """Fail before importing ML libraries if the served artifacts differ."""
    expected = [(base / 'model.safetensors', pin['base_weights_sha256']),
                (adapter / 'adapters.safetensors', pin['adapter_sha256']),
                (adapter / 'adapter_config.json', pin['adapter_config_sha256'])]
    expected += [(base / name, value) for name, value in pin['base_metadata'].items()]
    for path, value in expected:
        if file_hash(path) != value:
            raise ValueError(f'Model pin mismatch: {path.name}')
    config = json.loads((adapter / 'adapter_config.json').read_text())
    if config['base_model_name_or_path'] != pin['base_repo']:
        raise ValueError('Adapter does not name the pinned base model')
    return config


class ContextTooLong(ValueError):
    pass


class MLXEngine:
    def __init__(self, pin, base, adapter):
        self.pin = pin
        self.base = Path(base).resolve()
        self.adapter = Path(adapter).resolve()
        config = verify_files(pin, self.base, self.adapter)
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['UNSLOTH_MLX_PROMPT_CACHE_BYTES'] = '0'
        # The installed loader reads the adapter JSON itself. Stage a private
        # execution copy with an exact local base path instead of resolving a
        # mutable Hub branch; never modify the original adapter/configuration.
        self.staged = tempfile.TemporaryDirectory(prefix='narratryx-inference-')
        stage = Path(self.staged.name)
        for source in self.adapter.iterdir():
            if source.is_file() and source.name != 'adapter_config.json':
                (stage / source.name).symlink_to(source)
        config['base_model_name_or_path'] = str(self.base)
        (stage / 'adapter_config.json').write_text(json.dumps(config))
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='narratryx-mlx')
        try:
            self.executor.submit(self._load, stage).result()
        except BaseException:
            self.executor.shutdown(wait=True)
            self.staged.cleanup()
            raise

    def _load(self, stage):
        from unsloth_cli._inference import ensure_studio_backend_path, resolve_model_config
        ensure_studio_backend_path()
        from core.inference.mlx_inference import MLXInferenceBackend, _mlx_adapter_modules
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.base), local_files_only=True, trust_remote_code=False)
        self.backend = MLXInferenceBackend()
        config = resolve_model_config(str(stage), hf_token=None)
        if not config.is_lora or Path(config.base_model).resolve() != self.base:
            raise ValueError('Serving loader did not resolve the pinned local base')
        if not self.backend.load_model(config, max_seq_length=self.pin['context_limit'], load_in_4bit=False, trust_remote_code=False):
            raise RuntimeError('Pinned model failed to load')
        modules, unsupported = _mlx_adapter_modules(self.backend._model)
        if not modules or unsupported:
            self.backend.unload_model(self.backend.active_model_name)
            raise RuntimeError('Serving backend cannot control all adapter modules')

    def generate(self, messages, model, max_tokens, temperature, cancel):
        return self.executor.submit(self._generate, messages, model, max_tokens, temperature, cancel).result()

    def _generate(self, messages, model, max_tokens, temperature, cancel):
        encoded = self.tokenizer.apply_chat_template(messages, tokenize=True, return_dict=True,
                                                     add_generation_prompt=True, enable_thinking=False)
        # Transformers 5 returns BatchEncoding by default; its len() counts
        # fields rather than tokens. Count the explicit token sequence.
        ids = encoded['input_ids']
        if len(ids) + max_tokens > self.pin['context_limit']:
            raise ContextTooLong('This experimental model needs a shorter passage or less project context. Nothing was truncated or changed.')
        if self.backend._prompt_cache() is not None:
            raise RuntimeError('Experimental inference requires an empty prompt cache')
        system = messages[0]['content'] if messages[0]['role'] == 'system' else ''
        turns = messages[1:] if system else messages
        text = ''
        for chunk in self.backend.generate_with_adapter_control(
            use_adapter=model == self.pin['model_id'], messages=turns, system_prompt=system,
            tools=None, cancel_event=cancel, temperature=temperature, top_p=1, top_k=20, min_p=0,
            presence_penalty=0, repetition_penalty=1, seed=42, max_new_tokens=max_tokens, enable_thinking=False,
        ):
            if isinstance(chunk, str):
                text = str(chunk)
        if cancel.is_set():
            raise TimeoutError('Generation cancelled or exceeded its time limit')
        if not text.strip():
            raise RuntimeError('The model returned an empty response')
        stats = self.backend.last_generation_stats
        return dict(text=text, usage=stats.get('usage', {}), finish_reason=stats.get('finish_reason', 'stop'))

    def close(self):
        try:
            self.executor.submit(self.backend.unload_model, self.backend.active_model_name).result()
        finally:
            self.executor.shutdown(wait=True)
            self.staged.cleanup()
