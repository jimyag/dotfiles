#!/bin/bash
set -euo pipefail

if [ "${VPS:-}" = "1" ]; then
    echo "skip Go tool installation on VPS host" >&2
    exit 0
fi

if ! command -v go >/dev/null 2>&1; then
    echo "skip Go tool installation: go not found" >&2
    exit 0
fi

gobin="$(go env GOPATH)/bin"
mkdir -p "$gobin"
export PATH="$gobin:$PATH"

install_tool() {
    local binary="$1"
    local pkg="$2"
    local spec="$pkg@latest"

    echo "install $binary from $spec" >&2
    if GOBIN="$gobin" go install "$spec"; then
        return 0
    fi

    echo "warning: failed to install $binary from $spec" >&2
    return 1
}

failures=()

install_or_record() {
    if ! install_tool "$@"; then
        failures+=("$1")
    fi
}

install_or_record actionlint github.com/rhysd/actionlint/cmd/actionlint
install_or_record asmfmt github.com/klauspost/asmfmt/cmd/asmfmt
install_or_record authy-cli github.com/jimyag/authy-go/app/authy-cli
install_or_record bson2json github.com/ma6174/bsonex/tools/bson2json
install_or_record cmd-demo github.com/jimyag/cmd-demo
install_or_record cobra-cli github.com/spf13/cobra-cli
install_or_record comet github.com/liamg/comet
install_or_record deadcode golang.org/x/tools/cmd/deadcode
install_or_record dive github.com/wagoodman/dive
install_or_record dlv github.com/go-delve/delve/cmd/dlv
install_or_record docker-ls github.com/mayflower/docker-ls/cli/docker-ls
install_or_record docker-rm github.com/mayflower/docker-ls/cli/docker-rm
install_or_record formattag github.com/momaek/formattag
install_or_record fstail github.com/alexellis/fstail
install_or_record gdlv github.com/aarzilli/gdlv
install_or_record generators github.com/mayflower/docker-ls/generators
install_or_record ginkgo github.com/onsi/ginkgo/v2/ginkgo
install_or_record go-callvis github.com/ofabry/go-callvis
install_or_record go-getter github.com/hashicorp/go-getter/cmd/go-getter
install_or_record go-junit-report github.com/jstemmer/go-junit-report/v2
install_or_record gocyclo github.com/fzipp/gocyclo/cmd/gocyclo
install_or_record gofumpt mvdan.cc/gofumpt
install_or_record goimports golang.org/x/tools/cmd/goimports
install_or_record golangci-lint github.com/golangci/golangci-lint/v2/cmd/golangci-lint
install_or_record gomodifytags github.com/fatih/gomodifytags
install_or_record goplay github.com/haya14busa/goplay/cmd/goplay
install_or_record gopls golang.org/x/tools/gopls
install_or_record goreleaser github.com/goreleaser/goreleaser/v2
install_or_record gosec github.com/securego/gosec/v2/cmd/gosec
install_or_record gotests github.com/cweill/gotests/gotests
install_or_record hugo github.com/gohugoio/hugo
install_or_record impl github.com/josharian/impl
install_or_record kubebuilder sigs.k8s.io/kubebuilder/v4
install_or_record mockgen go.uber.org/mock/mockgen
install_or_record nats github.com/nats-io/natscli/nats
install_or_record nilaway go.uber.org/nilaway/cmd/nilaway
install_or_record parquet-tools github.com/jimyag/parquet-tools
install_or_record pproftui github.com/Oloruntobi1/pproftui
install_or_record protoc-gen-go google.golang.org/protobuf/cmd/protoc-gen-go
install_or_record protoc-gen-go-grpc google.golang.org/grpc/cmd/protoc-gen-go-grpc
install_or_record protoc-gen-go-vtproto github.com/planetscale/vtprotobuf/cmd/protoc-gen-go-vtproto
install_or_record protoc-go-inject-tag github.com/favadi/protoc-go-inject-tag
install_or_record qshell github.com/qiniu/qshell/v2/main
if [ -x "$gobin/main" ]; then
    mv "$gobin/main" "$gobin/qshell"
fi
install_or_record reflex github.com/cespare/reflex
install_or_record regctl github.com/regclient/regclient/cmd/regctl
install_or_record registry github.com/distribution/distribution/v3/cmd/registry
install_or_record staticcheck honnef.co/go/tools/cmd/staticcheck
install_or_record structlayout honnef.co/go/tools/cmd/structlayout
install_or_record tailoplog github.com/ma6174/tailoplog
install_or_record task github.com/go-task/task/v3/cmd/task
install_or_record tfplugindocs github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs

if [ -x "$gobin/golangci-lint" ]; then
    cp "$gobin/golangci-lint" "$gobin/golangci-lint-v2"
fi

for binary in portzero struct2json sparkctl; do
    if [ ! -x "$gobin/$binary" ]; then
        echo "warning: $binary requires local source or a copied binary; skip automatic install" >&2
    fi
done

if [ "${#failures[@]}" -gt 0 ]; then
    printf 'warning: failed Go tool installs: %s\n' "${failures[*]}" >&2
fi
