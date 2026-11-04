"""Download only the official Ref2VA model; keep partial bytes beside the target."""
import concurrent.futures
import hashlib
import json
import pathlib
import time
import urllib.request

NAME = 'minimax_h3_ref2va_pruned_int8_convrot.safetensors'
SIZE = 20970379616
SHA256 = '9255f52b6677845ad238f20dfaafa94727053694127ab7f255c048f0f9365779'
URL = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/' + NAME

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('models', type=pathlib.Path)
    args = parser.parse_args()
    target = args.models / 'diffusion_models' / NAME
    partial = target.with_suffix('.safetensors.partial')
    state = target.with_suffix('.safetensors.download.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    block = 16 * 1024 * 1024
    done = set(json.loads(state.read_text()) if state.exists() and partial.exists() else [])
    if not target.exists():
        if not partial.exists():
            with partial.open('wb') as f:
                f.truncate(SIZE)
        def chunk(start):
            end = min(start + block, SIZE) - 1
            for attempt in range(5):
                try:
                    request = urllib.request.Request(URL + '?chunk=' + str(start), headers={'Range': f'bytes={start}-{end}'})
                    with urllib.request.urlopen(request, timeout=90) as r:
                        if r.status != 206 or r.headers.get('Content-Range') != f'bytes {start}-{end}/{SIZE}':
                            raise ValueError('Unexpected range response')
                        data = r.read()
                    if len(data) != end - start + 1:
                        raise ValueError('Truncated range')
                    with partial.open('r+b') as f:
                        f.seek(start)
                        f.write(data)
                    return start
                except Exception:
                    if attempt == 4:
                        raise
                    time.sleep(attempt + 1)
        starts = list(range(0, SIZE, block))
        last = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            futures = [pool.submit(chunk, s) for s in starts if s not in done]
            for future in concurrent.futures.as_completed(futures):
                done.add(future.result())
                if time.monotonic() - last > 20 or len(done) == len(starts):
                    state.write_text(json.dumps(sorted(done)))
                    print(f'{len(done)}/{len(starts)} chunks ({len(done)/len(starts):.1%})', flush=True)
                    last = time.monotonic()
        source = partial
    else:
        source = target
    print('Verifying SHA-256...', flush=True)
    digest = hashlib.sha256()
    with source.open('rb') as f:
        while data := f.read(8 * 1024 * 1024):
            digest.update(data)
    if digest.hexdigest() != SHA256:
        raise ValueError('SHA-256 mismatch; file has not been activated')
    if source != target:
        partial.replace(target)
    state.unlink(missing_ok=True)
    print('VERIFIED ' + str(target), flush=True)

if __name__ == '__main__':
    main()
