import torch
import torchaudio
import os
import uuid
import folder_paths


class SkipAudioStart:
    """
    ComfyUI Custom Node: Skip Audio Start
    앞부분을 지정한 초만큼 건너뛰고, 나머지 전체를 출력합니다.
    미리듣기(Preview) 기능 포함.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "skip_seconds": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 9999.0,
                        "step": 0.1,
                        "display": "number",
                    },
                ),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "skip_audio"
    CATEGORY = "audio"
    OUTPUT_NODE = True  # 미리듣기 활성화

    def skip_audio(self, audio, skip_seconds: float):
        waveform = audio["waveform"]   # shape: (batch, channels, samples)
        sample_rate = audio["sample_rate"]

        skip_samples = int(skip_seconds * sample_rate)
        total_samples = waveform.shape[-1]

        if skip_samples >= total_samples:
            trimmed = torch.zeros(
                waveform.shape[0], waveform.shape[1], 1, dtype=waveform.dtype
            )
        else:
            trimmed = waveform[:, :, skip_samples:]

        result_audio = {"waveform": trimmed, "sample_rate": sample_rate}

        # ── 시간 정보 출력 ──────────────────────────────────
        remaining_duration = trimmed.shape[-1] / sample_rate
        original_duration = total_samples / sample_rate
        print(
            f"[SkipAudioStart] 원본: {original_duration:.2f}s | "
            f"스킵: {skip_seconds:.2f}s | "
            f"결과: {remaining_duration:.2f}s"
        )

        # ── 노드 자체 미리듣기용 임시 파일 저장 ──────────────
        preview = []
        try:
            temp_dir = folder_paths.get_temp_directory()
            os.makedirs(temp_dir, exist_ok=True)
            filename = f"skip_audio_preview_{uuid.uuid4().hex[:8]}.flac"
            filepath = os.path.join(temp_dir, filename)

            # (batch, channels, samples) → (channels, samples) 첫 배치만
            save_waveform = trimmed[0]
            torchaudio.save(filepath, save_waveform, sample_rate, format="flac")

            preview = [
                {
                    "filename": filename,
                    "subfolder": "",
                    "type": "temp",
                }
            ]
        except Exception as e:
            print(f"[SkipAudioStart] 미리듣기 저장 실패: {e}")

        return {"ui": {"audio": preview}, "result": (result_audio,)}


NODE_CLASS_MAPPINGS = {
    "SkipAudioStart": SkipAudioStart,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SkipAudioStart": "Skip Audio Start 🎵",
}
