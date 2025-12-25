#!/bin/bash

# 同步公开 dotfiles 仓库的配置到私有仓库
# 自动为公开仓库的文件创建软链接，跳过已存在的私有文件

set -euo pipefail

# 获取脚本所在目录的父目录（chezmoi 根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHEZMOI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PUBLIC_REPO_DIR="$CHEZMOI_ROOT/public_dotfiles"
PRIVATE_HOME_DIR="$CHEZMOI_ROOT/home"
PUBLIC_HOME_DIR="$PUBLIC_REPO_DIR/home"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查子模块是否存在
if [ ! -d "$PUBLIC_REPO_DIR" ]; then
    log_error "公开仓库目录不存在: $PUBLIC_REPO_DIR"
    log_info "请先添加子模块: git submodule add git@github.com:jimyag/dotfiles.git public_dotfiles"
    exit 1
fi

# 检查公开仓库的 home 目录是否存在
if [ ! -d "$PUBLIC_HOME_DIR" ]; then
    log_error "公开仓库的 home 目录不存在: $PUBLIC_HOME_DIR"
    log_info "请确保公开仓库结构正确，应该包含 home/ 目录"
    exit 1
fi

# 初始化子模块（如果还未初始化）
if [ ! -f "$PUBLIC_REPO_DIR/.git" ]; then
    log_info "初始化子模块..."
    git submodule update --init --recursive || {
        log_error "子模块初始化失败"
        exit 1
    }
fi

# 更新子模块到最新版本
log_info "更新公开仓库..."
cd "$CHEZMOI_ROOT"
if git submodule update --remote public_dotfiles 2>/dev/null; then
    log_info "公开仓库已更新到最新版本"
else
    log_warn "更新公开仓库失败，继续使用当前版本"
fi

log_info "开始同步公开配置..."

# 统计信息
created_count=0
skipped_count=0
error_count=0
deleted_count=0

# 处理单个文件，创建软链接
process_file() {
    local public_path="$1"
    local relative_path="${public_path#$PUBLIC_HOME_DIR/}"
    local private_path="$PRIVATE_HOME_DIR/$relative_path"
    local parent_dir="$(dirname "$private_path")"

    # 检查私有仓库中是否已存在
    if [ -e "$private_path" ]; then
        # 如果已经是软链接，检查是否指向正确位置
        if [ -L "$private_path" ]; then
            local link_target="$(readlink "$private_path")"
            local expected_target="$(realpath -m "$public_path")"
            if [ "$link_target" != "$expected_target" ] && [ "$(realpath "$private_path")" != "$expected_target" ]; then
                log_warn "软链接已存在但指向不同位置: $relative_path"
                log_warn "  当前指向: $link_target"
                log_warn "  应该指向: $expected_target"
                ((skipped_count++))
            else
                ((skipped_count++))
            fi
        else
            log_warn "跳过已存在的私有文件: $relative_path"
            ((skipped_count++))
        fi
        return
    fi

    # 创建父目录（如果不存在）
    if [ ! -d "$parent_dir" ]; then
        mkdir -p "$parent_dir"
    fi

    # 创建软链接
    local relative_link="$(realpath --relative-to="$parent_dir" "$public_path")"
    if ln -s "$relative_link" "$private_path" 2>/dev/null; then
        log_info "创建软链接: $relative_path"
        ((created_count++))
    else
        log_error "创建软链接失败: $relative_path"
        ((error_count++))
    fi
}

# 使用 find 命令遍历所有文件（包括隐藏文件）
log_info "扫描公开仓库文件..."

# 使用 process substitution 避免子 shell 问题
# 临时禁用 set -e 以处理可能的空结果
set +e
while IFS= read -r -d '' public_path; do
    # 只处理普通文件，跳过目录和符号链接
    if [ -f "$public_path" ] && [ ! -L "$public_path" ]; then
        process_file "$public_path"
    fi
done < <(find "$PUBLIC_HOME_DIR" -type f -print0 2>/dev/null)
find_exit_code=$?
set -e

# 如果 find 没有找到文件，这是正常的（可能目录为空）
if [ $find_exit_code -ne 0 ] && [ $find_exit_code -ne 1 ]; then
    log_error "查找文件时出错"
fi

# 清理已删除的软链接
log_info "检查并清理已删除的软链接..."
set +e
while IFS= read -r -d '' private_path; do
    if [ -L "$private_path" ]; then
        relative_path="${private_path#$PRIVATE_HOME_DIR/}"
        expected_public_path="$PUBLIC_HOME_DIR/$relative_path"
        
        # 检查软链接指向的文件是否存在
        # 先尝试解析软链接的绝对路径
        parent_dir="$(dirname "$private_path")"
        link_target="$(readlink "$private_path")"
        
        # 解析为绝对路径
        if [[ "$link_target" == /* ]]; then
            resolved_target="$link_target"
        else
            # 相对路径，基于软链接所在目录解析
            resolved_target="$(cd "$parent_dir" && realpath "$link_target" 2>/dev/null || echo "")"
            if [ -z "$resolved_target" ]; then
                # realpath 可能不可用，手动拼接
                link_dir="$(cd "$parent_dir" && cd "$(dirname "$link_target")" 2>/dev/null && pwd || echo "")"
                if [ -n "$link_dir" ]; then
                    resolved_target="$link_dir/$(basename "$link_target")"
                fi
            fi
        fi
        
        # 检查软链接是否指向公开仓库，并且对应的文件已不存在
        if [[ "$resolved_target" == "$PUBLIC_HOME_DIR"/* ]] || [[ "$resolved_target" == "$PUBLIC_REPO_DIR"/* ]]; then
            if [ ! -f "$expected_public_path" ]; then
                if rm "$private_path" 2>/dev/null; then
                    log_info "删除已移除的软链接: $relative_path"
                    ((deleted_count++))
                    
                    # 尝试删除空的父目录（递归向上）
                    dir_to_check="$(dirname "$private_path")"
                    while [ -d "$dir_to_check" ] && [ "$dir_to_check" != "$PRIVATE_HOME_DIR" ]; do
                        if rmdir "$dir_to_check" 2>/dev/null; then
                            dir_to_check="$(dirname "$dir_to_check")"
                        else
                            break
                        fi
                    done
                else
                    log_error "删除软链接失败: $relative_path"
                    ((error_count++))
                fi
            fi
        fi
    fi
done < <(find "$PRIVATE_HOME_DIR" -type l -print0 2>/dev/null)
cleanup_exit_code=$?
set -e

# 输出统计信息
echo ""
log_info "同步完成！"
log_info "  创建软链接: $created_count"
log_info "  删除软链接: $deleted_count"
log_info "  跳过文件: $skipped_count"
if [ $error_count -gt 0 ]; then
    log_error "  错误数量: $error_count"
fi

