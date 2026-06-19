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

installed_module() {
    local binary="$1"
    go version -m "$binary" 2>/dev/null | awk '$1 == "mod" {print $2; exit}'
}

installed_version() {
    local binary="$1"
    go version -m "$binary" 2>/dev/null | awk '$1 == "mod" {print $3; exit}'
}

needs_install() {
    local binary="$1"
    local module="$2"
    local version="$3"
    local path="$gobin/$binary"

    if [ ! -x "$path" ]; then
        return 0
    fi

    if [ "$(installed_module "$path")" != "$module" ]; then
        return 0
    fi

    if [ "$version" != "latest" ] && [ "$(installed_version "$path")" != "$version" ]; then
        return 0
    fi

    return 1
}

install_tool() {
    local binary="$1"
    local module="$2"
    local pkg="$3"
    local version="$4"
    local spec="$pkg@$version"

    if ! needs_install "$binary" "$module" "$version"; then
        echo "skip $binary: already installed" >&2
        return 0
    fi

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

install_or_record actionlint github.com/rhysd/actionlint github.com/rhysd/actionlint/cmd/actionlint v1.7.12
install_or_record asmfmt github.com/klauspost/asmfmt github.com/klauspost/asmfmt/cmd/asmfmt v1.3.2
install_or_record authy-cli github.com/jimyag/authy-go github.com/jimyag/authy-go/app/authy-cli v0.3.1
install_or_record bson2json github.com/ma6174/bsonex github.com/ma6174/bsonex/tools/bson2json v1.2.4
install_or_record cmd-demo github.com/jimyag/cmd-demo github.com/jimyag/cmd-demo v0.0.1
install_or_record cobra-cli github.com/spf13/cobra-cli github.com/spf13/cobra-cli v1.3.0
install_or_record comet github.com/liamg/comet github.com/liamg/comet v0.0.5
install_or_record deadcode golang.org/x/tools golang.org/x/tools/cmd/deadcode latest
install_or_record dive github.com/wagoodman/dive github.com/wagoodman/dive v0.13.1
install_or_record dlv github.com/go-delve/delve github.com/go-delve/delve/cmd/dlv v1.26.0
install_or_record docker-ls github.com/mayflower/docker-ls github.com/mayflower/docker-ls/cli/docker-ls latest
install_or_record docker-rm github.com/mayflower/docker-ls github.com/mayflower/docker-ls/cli/docker-rm latest
install_or_record formattag github.com/momaek/formattag github.com/momaek/formattag v0.0.10
install_or_record fstail github.com/alexellis/fstail github.com/alexellis/fstail v0.0.0-20250917111842-2ab578ec2afb
install_or_record gdlv github.com/aarzilli/gdlv github.com/aarzilli/gdlv v1.11.1
install_or_record generators github.com/mayflower/docker-ls github.com/mayflower/docker-ls/generators latest
install_or_record ginkgo github.com/onsi/ginkgo/v2 github.com/onsi/ginkgo/v2/ginkgo v2.31.0
install_or_record go-callvis github.com/ofabry/go-callvis github.com/ofabry/go-callvis v0.7.1
install_or_record go-getter github.com/hashicorp/go-getter github.com/hashicorp/go-getter/cmd/go-getter v1.8.5
install_or_record go-junit-report github.com/jstemmer/go-junit-report/v2 github.com/jstemmer/go-junit-report/v2 v2.0.0
install_or_record gocyclo github.com/fzipp/gocyclo github.com/fzipp/gocyclo/cmd/gocyclo v0.6.0
install_or_record gofumpt mvdan.cc/gofumpt mvdan.cc/gofumpt v0.10.0
install_or_record goimports golang.org/x/tools golang.org/x/tools/cmd/goimports v0.44.0
install_or_record golangci-lint github.com/golangci/golangci-lint/v2 github.com/golangci/golangci-lint/v2/cmd/golangci-lint v2.11.3
install_or_record gomodifytags github.com/fatih/gomodifytags github.com/fatih/gomodifytags v1.17.0
install_or_record goplay github.com/haya14busa/goplay github.com/haya14busa/goplay/cmd/goplay v1.0.0
install_or_record gopls golang.org/x/tools/gopls golang.org/x/tools/gopls v0.22.0
install_or_record goreleaser github.com/goreleaser/goreleaser/v2 github.com/goreleaser/goreleaser/v2 v2.13.0
install_or_record gosec github.com/securego/gosec/v2 github.com/securego/gosec/v2/cmd/gosec latest
install_or_record gotests github.com/cweill/gotests github.com/cweill/gotests/gotests v1.6.0
install_or_record hugo github.com/gohugoio/hugo github.com/gohugoio/hugo v0.157.0
install_or_record impl github.com/josharian/impl github.com/josharian/impl v1.4.0
install_or_record kubebuilder sigs.k8s.io/kubebuilder/v4 sigs.k8s.io/kubebuilder/v4 v4.13.1
install_or_record mockgen go.uber.org/mock go.uber.org/mock/mockgen v0.6.0
install_or_record nats github.com/nats-io/natscli github.com/nats-io/natscli/nats v0.2.2
install_or_record nilaway go.uber.org/nilaway go.uber.org/nilaway/cmd/nilaway v0.0.0-20250419134303-061cb73ae8e8
install_or_record parquet-tools github.com/jimyag/parquet-tools github.com/jimyag/parquet-tools v1.1.1
install_or_record pproftui github.com/Oloruntobi1/pproftui github.com/Oloruntobi1/pproftui v0.0.0-20250709162510-08953a3bc425
install_or_record protoc-gen-go google.golang.org/protobuf google.golang.org/protobuf/cmd/protoc-gen-go v1.32.0
install_or_record protoc-gen-go-grpc google.golang.org/grpc/cmd/protoc-gen-go-grpc google.golang.org/grpc/cmd/protoc-gen-go-grpc v1.6.1
install_or_record protoc-gen-go-vtproto github.com/planetscale/vtprotobuf github.com/planetscale/vtprotobuf/cmd/protoc-gen-go-vtproto v0.6.0
install_or_record protoc-go-inject-tag github.com/favadi/protoc-go-inject-tag github.com/favadi/protoc-go-inject-tag v1.4.0
install_or_record qshell github.com/qiniu/qshell/v2 github.com/qiniu/qshell/v2/main v2.19.8
if [ -x "$gobin/main" ]; then
    mv "$gobin/main" "$gobin/qshell"
fi
install_or_record reflex github.com/cespare/reflex github.com/cespare/reflex v0.3.1
install_or_record regctl github.com/regclient/regclient github.com/regclient/regclient/cmd/regctl v0.5.7
install_or_record registry github.com/distribution/distribution/v3 github.com/distribution/distribution/v3/cmd/registry latest
install_or_record staticcheck honnef.co/go/tools honnef.co/go/tools/cmd/staticcheck v0.7.0
install_or_record structlayout honnef.co/go/tools honnef.co/go/tools/cmd/structlayout latest
install_or_record tailoplog github.com/ma6174/tailoplog github.com/ma6174/tailoplog v0.0.0-20220121031527-4694fe0c7362
install_or_record task github.com/go-task/task/v3 github.com/go-task/task/v3/cmd/task v3.50.0
install_or_record tfplugindocs github.com/hashicorp/terraform-plugin-docs github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs v0.25.0

if [ -x "$gobin/golangci-lint" ] && [ ! -x "$gobin/golangci-lint-v2" ]; then
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
