# ci-testing
This repository contains code for CI/CD and testing of MosaicML repos including [Composer](https://github.com/mosaicml/composer) and [Foundry](https://github.com/mosaicml/llm-foundry).

# Release Instructions

1. When bumping patch/minor/major, also select `Set as the latest release`.


## GPU Tests

You can select the GPU test version you'd like to use by setting the `ci_repo_ref` input in your calling workflow to the desired repo release/branch.

