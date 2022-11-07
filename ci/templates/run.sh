#!/bin/bash
# Run script for packer AMI builds

set -e
cd templates
echo "========== GPU-amd64 Build =========="
/root/packer build -var type=gpu -machine-readable template.json | tee gpu_amd64_build.log

echo "========== Artifacts =========="
export GPU_AMI_AMD64=`cat gpu_amd64_build.log | grep "artifact" | grep ",id," | cut -d "," -f 6 | cut -d ":" -f 2`
echo "GPU-amd64 AMI: ${GPU_AMI_AMD64}"
