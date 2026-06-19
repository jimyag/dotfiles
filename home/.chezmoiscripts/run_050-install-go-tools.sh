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

gobin="$(go env GOBIN)"
if [ -z "$gobin" ]; then
    gobin="$(go env GOPATH)/bin"
fi
mkdir -p "$gobin"
export PATH="$gobin:$PATH"

install_tool() {
    local binary="$1"
    local pkg="$2"
    local spec="$pkg@latest"

    if command -v "$binary" >/dev/null 2>&1; then
        echo "skip $binary install: command already exists" >&2
        return 0
    fi

    echo "install $binary from $spec" >&2
    if go install "$spec"; then
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

install_hugo_extended() {
    local spec="github.com/gohugoio/hugo@latest"

    echo "install hugo extended from $spec" >&2
    if CGO_ENABLED=1 go install -tags extended "$spec"; then
        return 0
    fi

    echo "warning: failed to install hugo extended from $spec" >&2
    return 1
}

install_hugo_extended_or_record() {
    if ! install_hugo_extended; then
        failures+=("hugo")
    fi
}

install_or_record actionlint github.com/rhysd/actionlint/cmd/actionlint
install_or_record act github.com/nektos/act
install_or_record croc github.com/schollz/croc/v10
install_or_record dive github.com/wagoodman/dive
install_or_record dlv github.com/go-delve/delve/cmd/dlv
install_or_record formattag github.com/momaek/formattag
install_or_record ginkgo github.com/onsi/ginkgo/v2/ginkgo
install_or_record gofumpt mvdan.cc/gofumpt
install_or_record goimports golang.org/x/tools/cmd/goimports
install_or_record golangci-lint github.com/golangci/golangci-lint/v2/cmd/golangci-lint
install_or_record gomodifytags github.com/fatih/gomodifytags
install_or_record gopls golang.org/x/tools/gopls
install_or_record goreleaser github.com/goreleaser/goreleaser/v2
install_or_record gotests github.com/cweill/gotests/gotests
install_hugo_extended_or_record
install_or_record impl github.com/josharian/impl
install_or_record kind sigs.k8s.io/kind
install_or_record kubebuilder sigs.k8s.io/kubebuilder/v4
install_or_record mockgen go.uber.org/mock/mockgen
install_or_record protoc-gen-go google.golang.org/protobuf/cmd/protoc-gen-go
install_or_record protoc-gen-go-grpc google.golang.org/grpc/cmd/protoc-gen-go-grpc
install_or_record protoc-gen-go-vtproto github.com/planetscale/vtprotobuf/cmd/protoc-gen-go-vtproto
install_or_record qshell github.com/qiniu/qshell/v2/main
if [ -x "$gobin/main" ]; then
    mv "$gobin/main" "$gobin/qshell"
fi
install_or_record staticcheck honnef.co/go/tools/cmd/staticcheck
install_or_record task github.com/go-task/task/v3/cmd/task

if [ -x "$gobin/golangci-lint" ]; then
    cp "$gobin/golangci-lint" "$gobin/golangci-lint-v2"
fi

if [ "${#failures[@]}" -gt 0 ]; then
    printf 'warning: failed Go tool installs: %s\n' "${failures[*]}" >&2
fi
