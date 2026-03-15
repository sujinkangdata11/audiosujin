import torch
import torchaudio
import numpy as np


class SkipAudioStart:
    """
    ComfyUI Custom Node: Skip Audio Start
    앞부분을 지정한 초만큼 건너뛰고, 나머지를 출력합니다.
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
    OUTPUT_NODE = True  # 미리듣기(preview) 활성화

    def skip_audio(self, audio, skip_seconds: float):
        waveform = audio["waveform"]   # shape: (batch, channels, samples)
        sample_rate = audio["sample_rate"]

        skip_samples = int(skip_seconds * sample_rate)
        total_samples = waveform.shape[-1]

        if skip_samples >= total_samples:
            # 건너뛸 구간이 전체보다 크면 빈 오디오 반환
            empty = torch.zeros(
                waveform.shape[0], waveform.shape[1], 1, dtype=waveform.dtype
            )
            result_audio = {"waveform": empty, "sample_rate": sample_rate}
        else:
            trimmed = waveform[:, :, skip_samples:]
            result_audio = {"waveform": trimmed, "sample_rate": sample_rate}

        # ── 미리듣기용 정보 계산 ──────────────────────────────────
        remaining_samples = result_audio["waveform"].shape[-1]
        remaining_duration = remaining_samples / sample_rate
        original_duration = total_samples / sample_rate

        print(
            f"[SkipAudioStart] 원본: {original_duration:.2f}s | "
            f"스킵: {skip_seconds:.2f}s | "
            f"결과: {remaining_duration:.2f}s"
        )

        return (result_audio,)


NODE_CLASS_MAPPINGS = {
    "SkipAudioStart": SkipAudioStart,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SkipAudioStart": "Skip Audio Start 🎵",
}
