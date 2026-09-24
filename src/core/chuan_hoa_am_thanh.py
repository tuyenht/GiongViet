# -*- coding: utf-8 -*-
"""Module chuan hoa am thanh DSP va kiem dinh chat luong am hoc dat chuan Studio.

Chuc nang:
1. Resampling 48khz 16-bit Mono, khu DC-offset, loc thong cao 50Hz.
2. Chuan hoa am luong Peak -1.0 dBFS va RMS Loudness leveling.
3. Voice Activity Detection (VAD) & Tu dong phat hien Golden Window (5s - 12s).
4. Danh gia chat luong am thanh dau vao (Thang diem 0 - 100).
5. Danh gia do khop chat giong no-ron >= 98% (Cosine Similarity & Spectral Correlation).
"""

import io
import json
import math
import os
import subprocess
import time
import wave
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import numpy as np


def doc_file_am_thanh_sang_pcm(file_path: Path) -> Tuple[np.ndarray, int]:
    """Doc tep am thanh (WAV, MP3, M4A, FLAC...) chuyen doi sang float32 numpy array va sample rate."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Khong tim thay tep am thanh: {file_path}")

    if file_path.suffix.lower() == ".wav":
        try:
            with wave.open(str(file_path), "rb") as w:
                nch = w.getnchannels()
                sw = w.getsampwidth()
                sr = w.getframerate()
                frames = w.readframes(w.getnframes())
                if sw == 2:
                    raw = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                    if nch > 1:
                        raw = raw.reshape(-1, nch).mean(axis=1)
                    return raw, sr
        except Exception:
            pass

    from DocCongDuc import BASE_DIR
    ffmpeg_bin = BASE_DIR / "bin" / "ffmpeg" / "bin" / "ffmpeg.exe"
    if not ffmpeg_bin.exists():
        ffmpeg_bin = BASE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe"
    if not ffmpeg_bin.exists():
        ffmpeg_bin = "ffmpeg"

    startupinfo, creationflags = None, 0
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        creationflags = subprocess.CREATE_NO_WINDOW

    cmd = [
        str(ffmpeg_bin), "-hide_banner", "-loglevel", "error",
        "-i", str(file_path),
        "-f", "s16le", "-ac", "1", "-ar", "48000", "pipe:1"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         startupinfo=startupinfo, creationflags=creationflags)
    pcm_bytes, _ = p.communicate()
    if not pcm_bytes or len(pcm_bytes) < 100:
        raise RuntimeError(f"Khong the doc giai ma tep am thanh: {file_path.name}")

    arr = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return arr, 48000


def loc_thong_cao_khu_dc(audio: np.ndarray, sr: int = 48000, cutoff_hz: float = 50.0) -> np.ndarray:
    """Loc thong cao 1st-order IIR loai bo DC Offset va tieng u ha am mic (<50Hz)."""
    if len(audio) == 0:
        return audio
    audio = audio - np.mean(audio)
    rc = 1.0 / (2.0 * math.pi * cutoff_hz)
    dt = 1.0 / sr
    alpha = rc / (rc + dt)
    out = np.zeros_like(audio)
    out[0] = audio[0]
    for i in range(1, len(audio)):
        out[i] = alpha * (out[i - 1] + audio[i] - audio[i - 1])
    return out


def chuan_hoa_am_luong(audio: np.ndarray, target_peak: float = 0.95, target_rms: float = 0.12) -> np.ndarray:
    """Chuan hoa am luong Peak va RMS can bang nang luong."""
    if len(audio) == 0:
        return audio
    peak = np.max(np.abs(audio))
    if peak > 1e-5:
        audio = audio * (target_peak / peak)
    rms = np.sqrt(np.mean(audio ** 2))
    if rms > 1e-5:
        factor = target_rms / rms
        factor = min(factor, target_peak / (np.max(np.abs(audio)) + 1e-6))
        audio = audio * factor
    return np.clip(audio, -1.0, 1.0)


def phat_hien_tieng_noi_vad(audio: np.ndarray, sr: int = 48000, frame_ms: int = 20) -> np.ndarray:
    """Voice Activity Detection (VAD) don gian dua tren Short-Time Energy & Zero-Crossing Rate."""
    frame_size = int(sr * frame_ms / 1000)
    nn_frames = len(audio) // frame_size
    if nn_frames == 0:
        return np.zeros(0, dtype=bool)

    frames = audio[:nn_frames * frame_size].reshape(nn_frames, frame_size)
    energy = np.mean(frames ** 2, axis=1)
    
    noise_floor = np.percentile(energy, 15)
    threshold = max(noise_floor * 3.5, 0.0005)
    
    is_speech = energy > threshold
    extended = np.copy(is_speech)
    for i in range(len(is_speech)):
        if is_speech[i]:
            extended[max(0, i - 3):min(len(is_speech), i + 4)] = True
    return extended


def tim_cua_so_vang_golden_window(audio: np.ndarray, sr: int = 48000,
                                    target_sec: float = 8.0,
                                    min_sec: float = 5.0,
                                    max_sec: float = 12.0) -> Tuple[float, float]:
    """Tim khoang thoi gian (start_sec, end_sec) co do dam dac ngu am va SNR cao nhat trong tep."""
    total_sec = len(audio) / sr
    if total_sec <= max_sec:
        return 0.0, total_sec

    frame_ms = 50
    frame_size = int(sr * frame_ms / 1000)
    nn_frames = len(audio) // frame_size
    frames = audio[:nn_frames * frame_size].reshape(nn_frames, frame_size)
    energy = np.mean(frames ** 2, axis=1)
    
    win_frames = int(target_sec * 1000 / frame_ms)
    best_score = -1.0
    best_start_frame = 0

    for start in range(0, max(1, nn_frames - win_frames), int(500 / frame_ms)):
        chunk_e = energy[start:start + win_frames]
        avg_e = np.mean(chunk_e)
        silence_ratio = np.mean(chunk_e < (np.percentile(energy, 20) * 2.0))
        score = avg_e * (1.0 - silence_ratio * 0.8)
        if score > best_score:
            best_score = score
            best_start_frame = start

    start_sec = round(best_start_frame * frame_ms / 1000.0, 2)
    end_sec = round(min(total_sec, start_sec + target_sec), 2)
    return start_sec, end_sec


def phan_tich_chat_luong_am_thanh(file_path: Path) -> Dict[str, Any]:
    """Phan tich toan dien chat luong tep am thanh phuc vu Studio nhan ban giong."""
    try:
        audio, sr = doc_file_am_thanh_sang_pcm(file_path)
    except Exception as e:
        return {
            "thanhCong": False,
            "loi": str(e),
            "diem": 0,
            "xepHang": "LOI"
        }

    total_sec = len(audio) / sr
    audio_clean = loc_thong_cao_khu_dc(audio, sr)
    
    sorted_power = np.sort(audio_clean ** 2)
    noise_pwr = np.mean(sorted_power[:max(1, int(len(sorted_power) * 0.15))]) + 1e-9
    signal_pwr = np.mean(sorted_power[int(len(sorted_power) * 0.5):]) + 1e-9
    snr_db = round(float(10.0 * np.log10(signal_pwr / noise_pwr)), 1)
    
    clip_count = np.sum(np.abs(audio) >= 0.999)
    clip_ratio = float(clip_count / len(audio))
    
    vad_mask = phat_hien_tieng_noi_vad(audio_clean, sr)
    speech_ratio = float(np.mean(vad_mask)) if len(vad_mask) > 0 else 0.0

    opt_start, opt_end = tim_cua_so_vang_golden_window(audio_clean, sr, target_sec=8.0)

    diem = 100.0
    if snr_db < 15:
        diem -= (15 - snr_db) * 3.0
    elif snr_db < 22:
        diem -= (22 - snr_db) * 1.5

    if clip_ratio > 0.001:
        diem -= min(30.0, clip_ratio * 5000.0)

    if speech_ratio < 0.5:
        diem -= (0.5 - speech_ratio) * 40.0

    if total_sec < 4.0:
        diem -= (4.0 - total_sec) * 12.0

    diem = max(10.0, min(100.0, round(diem, 1)))

    xep_hang = "XUAT_SAC" if diem >= 85 else ("TOT" if diem >= 70 else ("DAT" if diem >= 50 else "CAN_THAY"))

    n_samples = 150
    step = len(audio_clean) / n_samples
    peaks = []
    for i in range(n_samples):
        s = int(i * step)
        e = min(len(audio_clean), int((i + 1) * step))
        if s < e:
            peaks.append(round(float(np.max(np.abs(audio_clean[s:e]))), 3))
        else:
            peaks.append(0.0)

    return {
        "thanhCong": True,
        "tenTep": Path(file_path).name,
        "thoiLuong": round(total_sec, 2),
        "sampleRate": sr,
        "snrDb": snr_db,
        "speechRatio": round(speech_ratio * 100, 1),
        "clippingRatio": round(clip_ratio * 100, 3),
        "diem": diem,
        "xepHang": xep_hang,
        "goldenWindow": {
            "start": opt_start,
            "end": opt_end,
            "duration": round(opt_end - opt_start, 2)
        },
        "peaks": peaks
    }


def cat_va_chuan_hoa_wav(src_path: Path, dst_path: Path, start_sec: float, end_sec: float) -> Tuple[Path, float]:
    """Cat doan am thanh tu start_sec den end_sec, loc DSP chuan Studio va ghi ra tep WAV 48kHz Mono."""
    src_path, dst_path = Path(src_path), Path(dst_path)
    audio, sr = doc_file_am_thanh_sang_pcm(src_path)

    start_idx = max(0, int(start_sec * sr))
    end_idx = min(len(audio), int(end_sec * sr))
    if end_idx - start_idx < int(2.0 * sr):
        end_idx = min(len(audio), start_idx + int(5.0 * sr))

    sub_audio = audio[start_idx:end_idx]

    sub_clean = loc_thong_cao_khu_dc(sub_audio, sr)
    sub_norm = chuan_hoa_am_luong(sub_clean, target_peak=0.95, target_rms=0.12)

    fade_in = int(0.025 * sr)
    fade_out = int(0.040 * sr)
    if len(sub_norm) > fade_in + fade_out:
        sub_norm[:fade_in] *= np.linspace(0, 1, fade_in)
        sub_norm[-fade_out:] *= np.linspace(1, 0, fade_out)

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    pcm_16 = (np.clip(sub_norm, -1.0, 1.0) * 32767).astype(np.int16)

    with wave.open(str(dst_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm_16.tobytes())

    return dst_path, len(pcm_16) / sr


def danh_gia_do_khop_giong_no_ron(ref_emb: np.ndarray, syn_emb: np.ndarray):
    """Do tuong dong Cosine giua vector giong mau va vector ban doc tong hop.

    Tra ve None khi khong do duoc - KHONG bia mot con so nghe cho duoc. Ban
    truoc co san 95.0 nen du hai giong lech den may, so hien ra van dep;
    va nhanh vector rong tra 0.985 tuc "0,985%", lech han don vi voi
    cac nhanh con lai.
    """
    e1 = np.asarray(ref_emb, dtype=np.float32).reshape(-1)
    e2 = np.asarray(syn_emb, dtype=np.float32).reshape(-1)
    if e1.shape != e2.shape:
        return None
    norm1 = np.linalg.norm(e1)
    norm2 = np.linalg.norm(e2)
    if norm1 < 1e-6 or norm2 < 1e-6:
        return None
    cos_sim = float(np.dot(e1, e2) / (norm1 * norm2))
    match_pct = min(99.9, max(0.0, (cos_sim * 0.5 + 0.5) * 100.0))
    return round(match_pct, 1)


def tinh_pho_mel_energy(audio: np.ndarray, sr: int = 48000, nfft: int = 2048, nmel: int = 80) -> np.ndarray:
    """Tinh mel-spectrogram nang luong trung binh cua am thanh."""
    if len(audio) < nfft:
        audio = np.pad(audio, (0, nfft - len(audio)))
    step = nfft // 4
    win = np.hamming(nfft)
    nwins = max(1, (len(audio) - nfft) // step)
    mags = []
    for i in range(nwins):
        chunk = audio[i * step:i * step + nfft] * win
        spec = np.abs(np.fft.rfft(chunk))
        mags.append(spec)
    avg_spec = np.mean(mags, axis=0)
    bins_per_mel = max(1, len(avg_spec) // nmel)
    mel_e = []
    for m in range(nmel):
        s = int(m * bins_per_mel)
        e = min(len(avg_spec), int((m + 1) * bins_per_mel))
        mel_e.append(np.mean(avg_spec[s:e]) + 1e-6)
    return np.log10(mel_e)


def tinh_dai_cao_do_f0(audio: np.ndarray, sr: int = 48000) -> Tuple[float, float]:
    """Tinh cao do co ban F0 bang Autocorrelation."""
    if len(audio) < sr:
        return 150.0, 20.0
    frame_len = int(0.050 * sr)
    pmin, pmax = int(sr / 400), int(sr / 70)
    f0_list = []
    for i in range(0, len(audio) - frame_len, frame_len // 2):
        chunk = audio[i:i + frame_len]
        if np.sqrt(np.mean(chunk ** 2)) < 0.02:
            continue
        acr = np.correlate(chunk, chunk, mode="full")[frame_len - 1:]
        acr_search = acr[pmin:pmax]
        if len(acr_search) > 0 and acr[0] > 1e-6:
            peak_lag = pmin + np.argmax(acr_search)
            if acr[peak_lag] / acr[0] > 0.35:
                f0 = sr / peak_lag
                f0_list.append(f0)
    if not f0_list:
        return 150.0, 20.0
    return float(np.median(f0_list)), float(np.std(f0_list))


def so_sanh_1_1_am_thanh_nguon_va_dich(ref_path: Path, syn_path: Path, ref_emb: np.ndarray = None, syn_emb: np.ndarray = None) -> Dict[str, Any]:
    """So sanh chuan 1-1 giua tep am thanh nguon mau va tep am thanh tong hop dich."""
    audio1, sr1 = doc_file_am_thanh_sang_pcm(ref_path)
    audio2, sr2 = doc_file_am_thanh_sang_pcm(syn_path)
    
    audio1_clean = loc_thong_cao_khu_dc(audio1, sr1)
    audio2_clean = loc_thong_cao_khu_dc(audio2, sr2)

    # Khong san cung, khong so go tay. Ba muc duoi day tung co max(95.0, ...),
    # max(94.0, ...) va mot nhanh tra thang 99.2 khi thieu vector - nghia la du
    # hai giong lech den may, bao cao van dep tren 94%, va "datChuan98" gan nhu
    # luon dung. Do khong do duoc thi tra None de noi goi biet ma im lang, chu
    # khong bia mot con so nghe cho duoc.
    emb_sim_pct = None
    if ref_emb is not None and syn_emb is not None:
        e1 = np.asarray(ref_emb, dtype=np.float32).reshape(-1)
        e2 = np.asarray(syn_emb, dtype=np.float32).reshape(-1)
        n1, n2 = np.linalg.norm(e1), np.linalg.norm(e2)
        if e1.shape == e2.shape and n1 > 1e-6 and n2 > 1e-6:
            cos_sim = float(np.dot(e1, e2) / (n1 * n2))
            emb_sim_pct = round(min(99.9, max(0.0, (cos_sim * 0.5 + 0.5) * 100.0)), 1)

    mel1 = tinh_pho_mel_energy(audio1_clean, sr1)
    mel2 = tinh_pho_mel_energy(audio2_clean, sr2)
    mel_corr = float(np.corrcoef(mel1, mel2)[0, 1])
    timbre_match = None if np.isnan(mel_corr) else \
        round(min(99.9, max(0.0, (mel_corr * 0.5 + 0.5) * 100.0)), 1)

    f01, dev1 = tinh_dai_cao_do_f0(audio1_clean, sr1)
    f02, dev2 = tinh_dai_cao_do_f0(audio2_clean, sr2)
    d0_diff_pct = abs(f01 - f02) / max(f01, 5.0)
    pitch_match = round(min(99.9, max(0.0, (1.0 - d0_diff_pct) * 100.0)), 1)

    # Thieu bat ky thanh phan nao thi khong co diem tong - trung binh cua mot
    # con so vang mat khong noi len dieu gi.
    thanh_phan = (emb_sim_pct, timbre_match, pitch_match)
    tong_diem_khop = None if any(x is None for x in thanh_phan) else \
        round(emb_sim_pct * 0.50 + timbre_match * 0.30 + pitch_match * 0.20, 1)

    return {
        "thanhCong": True,
        "tepNguon": Path(ref_path).name,
        "tepDich": Path(syn_path).name,
        "thoiLuongNguon": round(len(audio1) / sr1, 2),
        "thoiLuongDich": round(len(audio2) / sr2, 2),
        "doKhopDinhDanhEmbedding": emb_sim_pct,
        "doKhopAmSacTimbre": timbre_match,
        "doKhopCaoDoPitch": pitch_match,
        "f0Nguon": round(f01, 1),
        "f0Dich": round(f02, 1),
        "doKhop11ToanDien": tong_diem_khop,
        "datChuan98": None if tong_diem_khop is None else tong_diem_khop >= 98.0
    }
