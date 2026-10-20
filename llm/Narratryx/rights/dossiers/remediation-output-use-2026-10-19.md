# Remediation training request — output-use review, 19 October 2026

The user instructed “proceed with training”. That supplies execution intent for
the proposed next experiment. It does not supply an account agreement, a legal
opinion or evidence of a permitted use of the synthetic teacher outputs.

## Official sources checked

1. [Europe Terms of Use](https://openai.com/policies/eu-terms-of-use/), page
   marked updated 16 January 2026; checked 19 October 2026. “Using our Services”
   restricts using generated output to develop competing models. The page covers
   individual use in the UK, EEA and Switzerland and points business users to a
   different agreement. Its output-ownership provision does not remove the
   restrictions on use.
2. [OpenAI Services Agreement](https://openai.com/policies/services-agreement/),
   checked 19 October 2026. Section 3.3(e) also restricts developing competing
   models with output, subject to a defined exception. The listed exception
   concerns certain private classification/organisation models and customising
   models supplied through OpenAI services.

These are public web terms, not evidence of the agreement applicable to this
user's account. No custom agreement, exception, account-specific permission or
legal interpretation establishing permission for this Qwen fiction-writing
fine-tune was available. This review does not declare all third-party
fine-tuning prohibited, determine that this model legally competes with OpenAI,
or make a final legal finding. It records why permission remains unresolved
under the user's requirement to verify training-material rights.

## Current dataset decision

The twelve examples in `data/remediation-v1.pending.jsonl` contain synthetic
Codex-authored contexts and targets. Original drafting, mechanical correctness,
user intent to train and earlier approval of 108 public-domain prose passages
do not independently establish permission to use these new outputs for this
purpose. The teacher review and separate pending rights record therefore remain
unapproved. No human reviewer status or contractual permission has been inferred
from the training instruction.

The existing release validator continues to refuse this dataset at its first
pending example. No training run, approval bypass, paid job or model upload was
launched. The approved Opie/Wray adapter remains available and unchanged.
Repeating its raw-prose run would be a different experiment; it would not address
the instruction-following defects the new examples were meant to teach.

## Ways to resolve the blocker

- Establish that the applicable agreement or written permission allows these
  generated contexts/targets to train this model; separately accept or revise
  their editorial quality and record the evidence through the normal release
  process.
- Replace them with independently human-authored examples or material whose
  licence and provenance permit the intended training. A simple rewrite or
  relabelling of the existing synthetic examples is not rights verification.
- Obtain a new teacher dataset with suitable output-use permissions and record
  the provider/model licence, output terms and editorial review before training.

All application versions remain unchanged. This is a source/terms review and a
recorded, blocked launch request, not another model experiment.
