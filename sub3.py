import argparse
import random
from pathlib import Path
from typing import List

import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

# -------------- 工具函数 -----------------
def load_seeds(seg_id: int) -> List[str]:
    """读取 give_data/{seg_id}_give.txt"""
    #path = Path(f"give_data/{seg_id}_give.txt")
    path = Path(f"give_data/3_give.txt")#{seg_id}_give.txt")
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def get_seed_batch(seeds: List[str], ptr: int, batch_size: int) -> tuple[List[str], int]:
    """
    轮流取 batch_size 条种子；到尾部后打乱再重头。
    返回 (batch, 新指针)
    """
    if ptr + batch_size > len(seeds):
        random.shuffle(seeds)
        ptr = 0
    batch = seeds[ptr: ptr + batch_size]
    return batch, ptr + batch_size


def safe_generate(
    model,
    tokenizer,
    prompt: str,
    gen_len: int,
    top_k: int,
    top_p: float,
    temperature: float,
) -> str:
    """确保 prompt+gen_len 不超过上下文；必要时截断并重建文本"""
    max_ctx = model.config.n_positions  # GPT-2 = 1024
    ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    if ids.size(1) > max_ctx - gen_len - 1:
        ids = ids[:, -(max_ctx - gen_len - 1) :]
        prompt = tokenizer.decode(ids[0], skip_special_tokens=False)

    out = model.generate(
        ids,
        max_new_tokens=gen_len,
        do_sample=True,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(out[0], skip_special_tokens=False)


# -------------- 主逻辑 -------------------
def run(
    model_dir: str,
    total_gen: int,
    batch_size: int,
    max_new_tokens: int,
    top_k: int,
    top_p: float,
    temperature: float,
    use_fp16: bool,
):
    # ---- 模型 ----
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_dir, local_files_only=True).cuda()

    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id
    model.eval()

    if torch.cuda.is_available():
        model.to("cuda")
        if use_fp16:
            model.half()

    all_results, all_seen = [], set()
    per_seg_target = min(total_gen // 4, 5_000)

    for seg in range(1, 2):
        seeds = load_seeds(seg)
        seen = set(seeds)
        uniq = []
        ptr = 0
        pbar = tqdm(total=per_seg_target, desc=f"seg{seg}", unit="addr")

        while len(uniq) < per_seg_target:
            batch, ptr = get_seed_batch(seeds, ptr, batch_size)
            prompt = "".join(f"<seg{seg}> {addr}\n" for addr in batch)
            text = safe_generate(
                model, tokenizer, prompt, max_new_tokens, top_k, top_p, temperature
            )

            for ln in text.split("\n"):
                ln = ln.strip()
                if not ln.startswith(f"<seg{seg}>"):
                    continue
                parts = ln.split(maxsplit=1)
                if len(parts) < 2:
                    continue
                addr = parts[1]
                if addr.startswith("2001:") and addr not in seen:
                    seen.add(addr)
                    uniq.append(addr)
                    pbar.update(1)
                    if len(uniq) >= per_seg_target:
                        break
        pbar.close()
        all_results.extend(uniq)
        all_seen.update(seen)

    # ---- 写文件 ----
    all_results = all_results[: min(total_gen, 5_000)]
    pd.Series(all_results).to_csv(
        "submission3.csv", index=False, header=False, encoding="utf-8"
    )
    print(f"\n🎉 已写入 {len(all_results)} 行 -> submission.csv")


# -------------- CLI ----------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", default="./openai-community---gpt2")
    parser.add_argument("--total_gen", type=int, default=1_000_000)
    parser.add_argument("--batch_size", type=int, default=2048)
    parser.add_argument("--max_new_tokens", type=int, default=256)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--temperature", type=float, default=1)
    parser.add_argument("--fp16", action="store_true", help="GPU 上用 half 精度省显存")
    args = parser.parse_args()

    run(
        model_dir=args.model_dir,
        total_gen=args.total_gen,
        batch_size=args.batch_size,
        max_new_tokens=args.max_new_tokens,
        top_k=args.top_k,
        top_p=args.top_p,
        temperature=args.temperature,
        use_fp16=args.fp16,
    )
