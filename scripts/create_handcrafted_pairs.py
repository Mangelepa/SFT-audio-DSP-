import json
import os

OUTPUT_FILE = "../data/handcrafted_pairs.jsonl"

# ── Handcrafted DSP Pairs ──────────────────────────────────────────────────────

PAIRS = [
    {
        "instruction": "How do I implement a low-pass filter in C++?",
        "response": """float lowPassFilter(float input, float& prevOutput, float cutoff, float sampleRate) {
    float rc = 1.0f / (2.0f * 3.14159f * cutoff);
    float dt = 1.0f / sampleRate;
    float alpha = dt / (rc + dt);
    prevOutput = prevOutput + alpha * (input - prevOutput);
    return prevOutput;
}

// This implements a first-order RC low-pass filter.
// alpha controls the cutoff: lower alpha = lower cutoff frequency.
// cutoff is in Hz, sampleRate is in Hz (e.g. 44100)."""
    },
    {
        "instruction": "How do I implement a high-pass filter in C++?",
        "response": """float highPassFilter(float input, float& prevInput, float& prevOutput, float cutoff, float sampleRate) {
    float rc = 1.0f / (2.0f * 3.14159f * cutoff);
    float dt = 1.0f / sampleRate;
    float alpha = rc / (rc + dt);
    prevOutput = alpha * (prevOutput + input - prevInput);
    prevInput  = input;
    return prevOutput;
}

// First-order high-pass filter. Passes frequencies above cutoff.
// Useful for removing DC offset or low-frequency rumble."""
    },
    {
        "instruction": "How do I implement a biquad filter in C++?",
        "response": """struct BiquadFilter {
    float b0, b1, b2, a1, a2;
    float x1 = 0, x2 = 0, y1 = 0, y2 = 0;

    float process(float x) {
        float y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
        x2 = x1; x1 = x;
        y2 = y1; y1 = y;
        return y;
    }

    void setLowPass(float cutoff, float Q, float sampleRate) {
        float w0    = 2.0f * 3.14159f * cutoff / sampleRate;
        float cosW0 = cosf(w0);
        float sinW0 = sinf(w0);
        float alpha = sinW0 / (2.0f * Q);
        float a0    = 1.0f + alpha;
        b0 = ((1.0f - cosW0) / 2.0f) / a0;
        b1 = (1.0f - cosW0) / a0;
        b2 = b0;
        a1 = (-2.0f * cosW0) / a0;
        a2 = (1.0f - alpha) / a0;
    }
};

// Biquad (second-order IIR) filter — the building block of most audio EQs.
// Supports low-pass, high-pass, band-pass, notch, shelf, and peaking modes."""
    },
    {
        "instruction": "How do I implement a simple delay effect in C++?",
        "response": """class DelayEffect {
    std::vector<float> buffer;
    int writePos = 0;
    int delaySamples;

public:
    DelayEffect(int delaySamples, int maxDelay = 44100)
        : buffer(maxDelay, 0.0f), delaySamples(delaySamples) {}

    float process(float input, float feedback = 0.5f, float mix = 0.5f) {
        int readPos  = (writePos - delaySamples + buffer.size()) % buffer.size();
        float delayed = buffer[readPos];
        buffer[writePos] = input + delayed * feedback;
        writePos = (writePos + 1) % buffer.size();
        return input * (1.0f - mix) + delayed * mix;
    }
};

// Simple circular buffer delay with feedback and wet/dry mix.
// delaySamples controls delay time, feedback controls echo decay."""
    },
    {
        "instruction": "How do I implement a reverb effect in C++?",
        "response": """class SimpleReverb {
    std::vector<float> combBuffer1, combBuffer2, combBuffer3, combBuffer4;
    int pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    float feedback;

public:
    SimpleReverb(float feedback = 0.7f)
        : combBuffer1(1557, 0), combBuffer2(1617, 0),
          combBuffer3(1491, 0), combBuffer4(1422, 0),
          feedback(feedback) {}

    float process(float input) {
        float out = 0.0f;
        out += processComb(combBuffer1, pos1, input);
        out += processComb(combBuffer2, pos2, input);
        out += processComb(combBuffer3, pos3, input);
        out += processComb(combBuffer4, pos4, input);
        return out * 0.25f;
    }

    float processComb(std::vector<float>& buf, int& pos, float input) {
        float out = buf[pos];
        buf[pos]  = input + out * feedback;
        pos       = (pos + 1) % buf.size();
        return out;
    }
};

// Schroeder reverb using parallel comb filters.
// Different buffer sizes create the diffuse reverb tail."""
    },
    {
        "instruction": "How do I implement an ADSR envelope in C++?",
        "response": """class ADSR {
public:
    enum State { IDLE, ATTACK, DECAY, SUSTAIN, RELEASE };

    float attack, decay, sustain, release, sampleRate;
    float currentLevel = 0.0f;
    State state = IDLE;

    ADSR(float a, float d, float s, float r, float sr)
        : attack(a), decay(d), sustain(s), release(r), sampleRate(sr) {}

    void noteOn()  { state = ATTACK; }
    void noteOff() { state = RELEASE; }

    float process() {
        switch (state) {
            case ATTACK:
                currentLevel += 1.0f / (attack * sampleRate);
                if (currentLevel >= 1.0f) { currentLevel = 1.0f; state = DECAY; }
                break;
            case DECAY:
                currentLevel -= (1.0f - sustain) / (decay * sampleRate);
                if (currentLevel <= sustain) { currentLevel = sustain; state = SUSTAIN; }
                break;
            case SUSTAIN:
                currentLevel = sustain;
                break;
            case RELEASE:
                currentLevel -= sustain / (release * sampleRate);
                if (currentLevel <= 0.0f) { currentLevel = 0.0f; state = IDLE; }
                break;
            default: break;
        }
        return currentLevel;
    }
};

// Classic ADSR envelope generator.
// attack/decay/release are in seconds, sustain is 0.0-1.0 amplitude level."""
    },
    {
        "instruction": "How do I implement an LFO in C++?",
        "response": """class LFO {
    float phase = 0.0f;
    float phaseIncrement;

public:
    enum Waveform { SINE, TRIANGLE, SQUARE, SAWTOOTH };
    Waveform waveform = SINE;

    LFO(float rate, float sampleRate) {
        phaseIncrement = rate / sampleRate;
    }

    void setRate(float rate, float sampleRate) {
        phaseIncrement = rate / sampleRate;
    }

    float process() {
        float out = 0.0f;
        switch (waveform) {
            case SINE:     out = sinf(2.0f * 3.14159f * phase); break;
            case TRIANGLE: out = 1.0f - 4.0f * fabsf(phase - 0.5f); break;
            case SQUARE:   out = phase < 0.5f ? 1.0f : -1.0f; break;
            case SAWTOOTH: out = 2.0f * phase - 1.0f; break;
        }
        phase += phaseIncrement;
        if (phase >= 1.0f) phase -= 1.0f;
        return out;
    }
};

// Low Frequency Oscillator with 4 waveforms.
// Rate is in Hz. Output range is -1.0 to 1.0."""
    },
    {
        "instruction": "How do I implement a compressor in C++?",
        "response": """class Compressor {
    float envelope = 0.0f;
    float attackCoeff, releaseCoeff;

public:
    float threshold, ratio, makeupGain;

    Compressor(float threshold, float ratio, float attack,
               float release, float makeup, float sampleRate)
        : threshold(threshold), ratio(ratio), makeupGain(makeup) {
        attackCoeff  = expf(-1.0f / (attack  * sampleRate));
        releaseCoeff = expf(-1.0f / (release * sampleRate));
    }

    float process(float input) {
        float inputLevel = fabsf(input);

        // Envelope follower
        if (inputLevel > envelope)
            envelope = attackCoeff  * envelope + (1.0f - attackCoeff)  * inputLevel;
        else
            envelope = releaseCoeff * envelope + (1.0f - releaseCoeff) * inputLevel;

        // Gain computation
        float gainDb = 0.0f;
        float envDb  = 20.0f * log10f(envelope + 1e-6f);
        if (envDb > threshold)
            gainDb = (threshold - envDb) * (1.0f - 1.0f / ratio);

        float gain = powf(10.0f, (gainDb + makeupGain) / 20.0f);
        return input * gain;
    }
};

// Dynamic range compressor with attack/release envelope follower.
// threshold in dB, ratio e.g. 4.0 for 4:1, makeup in dB."""
    },
    {
        "instruction": "How do I implement a distortion effect in C++?",
        "response": """class Distortion {
public:
    enum Type { HARDCLIP, SOFTCLIP, TANH, FOLDBACK };
    Type type = SOFTCLIP;
    float drive, mix;

    Distortion(float drive = 2.0f, float mix = 1.0f)
        : drive(drive), mix(mix) {}

    float process(float input) {
        float driven = input * drive;
        float distorted = 0.0f;

        switch (type) {
            case HARDCLIP:
                distorted = std::clamp(driven, -1.0f, 1.0f);
                break;
            case SOFTCLIP:
                distorted = driven / (1.0f + fabsf(driven));
                break;
            case TANH:
                distorted = tanhf(driven);
                break;
            case FOLDBACK:
                distorted = driven;
                while (fabsf(distorted) > 1.0f)
                    distorted = fabsf(fabsf(distorted) - 2.0f) - 1.0f;
                break;
        }
        return input * (1.0f - mix) + distorted * mix;
    }
};

// Waveshaping distortion with 4 modes.
// drive > 1.0 increases saturation, mix controls wet/dry blend."""
    },
    {
        "instruction": "How do I implement a sine wave oscillator in C++?",
        "response": """class SineOscillator {
    float phase = 0.0f;
    float phaseIncrement;
    float sampleRate;

public:
    SineOscillator(float sampleRate) : sampleRate(sampleRate) {
        setFrequency(440.0f);
    }

    void setFrequency(float freq) {
        phaseIncrement = freq / sampleRate;
    }

    float process() {
        float output = sinf(2.0f * 3.14159265f * phase);
        phase += phaseIncrement;
        if (phase >= 1.0f) phase -= 1.0f;
        return output;
    }
};

// Band-limited sine oscillator using phase accumulator method.
// setFrequency() in Hz, process() returns one sample at a time."""
    },
    {
        "instruction": "How do I convert decibels to gain in C++?",
        "response": """// Convert decibels to linear gain
float dBToGain(float dB) {
    return powf(10.0f, dB / 20.0f);
}

// Convert linear gain to decibels
float gainTodB(float gain) {
    return 20.0f * log10f(fabsf(gain) + 1e-9f);
}

// Apply gain in dB to a signal
float applyGainDB(float sample, float gainDB) {
    return sample * dBToGain(gainDB);
}

// Smooth gain changes to avoid clicks
class SmoothedGain {
    float currentGain = 1.0f;
    float smoothing;
public:
    SmoothedGain(float smoothingTimeMs, float sampleRate) {
        smoothing = expf(-1.0f / (smoothingTimeMs * 0.001f * sampleRate));
    }
    float process(float targetGain) {
        currentGain = smoothing * currentGain + (1.0f - smoothing) * targetGain;
        return currentGain;
    }
};

// Use 1e-9f offset in gainTodB to avoid log(0) when gain is zero."""
    },
    {
        "instruction": "How do I implement a band-pass filter in C++?",
        "response": """struct BandPassFilter {
    float b0, b1, b2, a1, a2;
    float x1 = 0, x2 = 0, y1 = 0, y2 = 0;

    void setCoefficients(float centerFreq, float Q, float sampleRate) {
        float w0    = 2.0f * 3.14159f * centerFreq / sampleRate;
        float cosW0 = cosf(w0);
        float sinW0 = sinf(w0);
        float alpha = sinW0 / (2.0f * Q);
        float a0    = 1.0f + alpha;
        b0 =  (sinW0 / 2.0f) / a0;
        b1 =  0.0f;
        b2 = -(sinW0 / 2.0f) / a0;
        a1 = (-2.0f * cosW0) / a0;
        a2 = (1.0f - alpha)  / a0;
    }

    float process(float x) {
        float y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2;
        x2 = x1; x1 = x;
        y2 = y1; y1 = y;
        return y;
    }
};

// Biquad band-pass filter. centerFreq in Hz, Q controls bandwidth.
// Higher Q = narrower band. Useful for formant filtering and EQ."""
    },
    {
        "instruction": "How do I implement a chorus effect in C++?",
        "response": """class Chorus {
    std::vector<float> delayBuffer;
    int writePos = 0;
    float lfoPhase = 0.0f;
    float sampleRate;

public:
    float rate, depth, mix;

    Chorus(float sampleRate, float rate = 1.0f,
           float depth = 0.002f, float mix = 0.5f)
        : sampleRate(sampleRate), rate(rate), depth(depth), mix(mix),
          delayBuffer(static_cast<int>(sampleRate * 0.05f), 0.0f) {}

    float process(float input) {
        // LFO modulates delay time
        float lfo = sinf(2.0f * 3.14159f * lfoPhase);
        lfoPhase += rate / sampleRate;
        if (lfoPhase >= 1.0f) lfoPhase -= 1.0f;

        // Modulated delay in samples
        float delaySamples = (0.02f + lfo * depth) * sampleRate;
        int   delayInt     = static_cast<int>(delaySamples);
        float frac         = delaySamples - delayInt;

        // Linear interpolation for fractional delay
        int readA = (writePos - delayInt + delayBuffer.size()) % delayBuffer.size();
        int readB = (readA - 1 + delayBuffer.size()) % delayBuffer.size();
        float delayed = delayBuffer[readA] + frac * (delayBuffer[readB] - delayBuffer[readA]);

        delayBuffer[writePos] = input;
        writePos = (writePos + 1) % delayBuffer.size();

        return input * (1.0f - mix) + delayed * mix;
    }
};

// Chorus using LFO-modulated delay with linear interpolation.
// rate in Hz controls LFO speed, depth controls modulation amount."""
    },
    {
        "instruction": "How do I implement stereo panning in C++?",
        "response": """struct StereoPanner {
    float leftGain  = 1.0f;
    float rightGain = 1.0f;

    // pan: -1.0 = full left, 0.0 = center, 1.0 = full right
    void setPan(float pan) {
        // Constant power panning (equal power law)
        float angle = (pan + 1.0f) * 0.25f * 3.14159f; // 0 to pi/2
        leftGain    = cosf(angle);
        rightGain   = sinf(angle);
    }

    void process(float input, float& left, float& right) {
        left  = input * leftGain;
        right = input * rightGain;
    }

    void processStereo(float inL, float inR, float& outL, float& outR) {
        outL = inL * leftGain;
        outR = inR * rightGain;
    }
};

// Constant power panner — maintains equal perceived loudness across the field.
// Uses cos/sin law so center pan gives -3dB to each side."""
    },
    {
        "instruction": "How do I implement a noise gate in C++?",
        "response": """class NoiseGate {
    float envelope  = 0.0f;
    float attackCoeff, releaseCoeff;
    bool  gateOpen  = false;

public:
    float threshold, attackTime, releaseTime;

    NoiseGate(float threshold, float attack, float release, float sampleRate)
        : threshold(threshold), attackTime(attack), releaseTime(release) {
        attackCoeff  = expf(-1.0f / (attack  * sampleRate));
        releaseCoeff = expf(-1.0f / (release * sampleRate));
    }

    float process(float input) {
        float level = fabsf(input);

        // Smooth envelope follower
        float coeff = level > envelope ? attackCoeff : releaseCoeff;
        envelope    = coeff * envelope + (1.0f - coeff) * level;

        // Hysteresis to prevent chattering
        if (!gateOpen && envelope > threshold)
            gateOpen = true;
        else if (gateOpen && envelope < threshold * 0.5f)
            gateOpen = false;

        return gateOpen ? input : 0.0f;
    }
};

// Noise gate with hysteresis to prevent rapid open/close chattering.
// threshold is linear amplitude, attack/release in seconds."""
    },
    {
        "instruction": "How do I apply gain to an audio signal in C++?",
        "response": """// Simple gain application
float applyGain(float sample, float gainLinear) {
    return sample * gainLinear;
}

// Apply gain to a buffer of samples
void applyGainToBuffer(float* buffer, int numSamples, float gainLinear) {
    for (int i = 0; i < numSamples; ++i)
        buffer[i] *= gainLinear;
}

// Smoothly ramp gain to avoid clicks
class GainRamp {
    float currentGain;
    float targetGain;
    float stepSize;

public:
    GainRamp(float initialGain = 1.0f) : currentGain(initialGain), targetGain(initialGain), stepSize(0.0f) {}

    void setGain(float newGain, int rampSamples) {
        targetGain = newGain;
        stepSize   = (newGain - currentGain) / rampSamples;
    }

    float process(float input) {
        if (fabsf(currentGain - targetGain) > fabsf(stepSize))
            currentGain += stepSize;
        else
            currentGain = targetGain;
        return input * currentGain;
    }
};

// GainRamp smooths gain transitions to avoid audible clicks or zippers."""
    },
    {
        "instruction": "How do I implement a limiter in C++ for audio?",
        "response": """class Limiter {
    float envelope  = 0.0f;
    float releaseCoeff;

public:
    float threshold, releaseTime;

    Limiter(float threshold = 1.0f, float release = 0.1f, float sampleRate = 44100.0f)
        : threshold(threshold), releaseTime(release) {
        releaseCoeff = expf(-1.0f / (release * sampleRate));
    }

    float process(float input) {
        float level = fabsf(input);

        // Peak detector with instant attack, smooth release
        if (level > envelope)
            envelope = level;
        else
            envelope = releaseCoeff * envelope + (1.0f - releaseCoeff) * level;

        // Compute gain reduction
        float gain = 1.0f;
        if (envelope > threshold)
            gain = threshold / envelope;

        return input * gain;
    }
};

// True peak limiter with instant attack and smooth release.
// threshold is linear amplitude (1.0 = 0 dBFS).
// Prevents any output sample from exceeding threshold."""
    },
    {
        "instruction": "How do I implement audio resampling in C++?",
        "response": """class LinearResampler {
    float prevSample = 0.0f;
    float phase      = 0.0f;
    float ratio;

public:
    // ratio = outputSampleRate / inputSampleRate
    LinearResampler(float inputRate, float outputRate)
        : ratio(inputRate / outputRate) {}

    // Call this for each output sample, feeding new input samples as needed
    float process(float newInputSample) {
        float output = prevSample + phase * (newInputSample - prevSample);
        phase += ratio;

        while (phase >= 1.0f) {
            prevSample = newInputSample;
            phase -= 1.0f;
        }
        return output;
    }

    void resampleBuffer(const float* input,  int inputLen,
                              float* output, int outputLen) {
        float inputPhase = 0.0f;
        float step       = (float)inputLen / (float)outputLen;
        for (int i = 0; i < outputLen; ++i) {
            int   idx  = (int)inputPhase;
            float frac = inputPhase - idx;
            int   next = std::min(idx + 1, inputLen - 1);
            output[i]  = input[idx] + frac * (input[next] - input[idx]);
            inputPhase += step;
        }
    }
};

// Linear interpolation resampler. Not the highest quality but fast and simple.
// For better quality, use sinc interpolation or polyphase filtering."""
    },
    {
        "instruction": "How do I implement pitch shifting in C++?",
        "response": """class PitchShifter {
    std::vector<float> buffer;
    float readPos  = 0.0f;
    int   writePos = 0;
    float pitchRatio;
    int   bufferSize;

public:
    PitchShifter(float pitchRatio, float sampleRate, float bufferMs = 50.0f)
        : pitchRatio(pitchRatio) {
        bufferSize = static_cast<int>(sampleRate * bufferMs * 0.001f);
        buffer.resize(bufferSize, 0.0f);
        readPos = 0.0f;
    }

    void setPitch(float semitones) {
        pitchRatio = powf(2.0f, semitones / 12.0f);
    }

    float process(float input) {
        buffer[writePos] = input;

        // Read with fractional index (linear interpolation)
        int   readInt  = static_cast<int>(readPos);
        float frac     = readPos - readInt;
        int   readNext = (readInt + 1) % bufferSize;
        float output   = buffer[readInt % bufferSize] * (1.0f - frac)
                       + buffer[readNext]              * frac;

        writePos = (writePos + 1) % bufferSize;
        readPos  = fmodf(readPos + pitchRatio, (float)bufferSize);

        return output;
    }
};

// Simple time-domain pitch shifter using circular buffer.
// setPitch() takes semitones: +12 = octave up, -12 = octave down."""
    },
    {
        "instruction": "How do I implement a waveshaper for audio distortion in C++?",
        "response": """class WaveShaper {
public:
    // Soft clip using cubic polynomial
    static float softClip(float x, float drive = 1.0f) {
        x *= drive;
        if (x >  1.0f) return  2.0f / 3.0f;
        if (x < -1.0f) return -2.0f / 3.0f;
        return x - (x * x * x) / 3.0f;
    }

    // Tube-style saturation
    static float tubeSaturation(float x, float drive = 2.0f) {
        x *= drive;
        return tanhf(x) / tanhf(drive);
    }

    // Asymmetric waveshaper (odd harmonics)
    static float asymmetricClip(float x, float drive = 1.0f) {
        x *= drive;
        if (x >= 0) return 1.0f - expf(-x);
        return       -1.0f + expf( x);
    }

    // Apply a custom lookup table waveshaper
    static float applyTable(float x, const float* table, int tableSize) {
        float normalized = (x + 1.0f) * 0.5f * (tableSize - 1);
        int   idx        = std::clamp((int)normalized, 0, tableSize - 2);
        float frac       = normalized - idx;
        return table[idx] + frac * (table[idx + 1] - table[idx]);
    }
};

// WaveShaper collection for audio distortion/saturation effects.
// softClip produces warm saturation, tubeSaturation emulates valve harmonics."""
    },
    {
        "instruction": "How do I implement a parametric equalizer in C++?",
        "response": """struct ParametricEQ {
    struct Band {
        float b0, b1, b2, a1, a2;
        float x1 = 0, x2 = 0, y1 = 0, y2 = 0;

        void setPeaking(float freq, float Q, float gainDB, float sampleRate) {
            float A    = powf(10.0f, gainDB / 40.0f);
            float w0   = 2.0f * 3.14159f * freq / sampleRate;
            float cosW = cosf(w0);
            float sinW = sinf(w0);
            float alpha = sinW / (2.0f * Q);
            float a0   = 1.0f + alpha / A;
            b0 = (1.0f + alpha * A) / a0;
            b1 = (-2.0f * cosW)     / a0;
            b2 = (1.0f - alpha * A) / a0;
            a1 = (-2.0f * cosW)     / a0;
            a2 = (1.0f - alpha / A) / a0;
        }

        float process(float x) {
            float y = b0*x + b1*x1 + b2*x2 - a1*y1 - a2*y2;
            x2 = x1; x1 = x;
            y2 = y1; y1 = y;
            return y;
        }
    };

    std::vector<Band> bands;

    ParametricEQ(int numBands) : bands(numBands) {}

    float process(float input) {
        float output = input;
        for (auto& band : bands)
            output = band.process(output);
        return output;
    }
};

// Multi-band parametric EQ using cascaded biquad filters.
// Each band has independent frequency, Q, and gain in dB."""
    },
    {
        "instruction": "How do I implement a phaser effect in C++?",
        "response": """class Phaser {
    struct AllPassFilter {
        float a1 = 0.0f, z1 = 0.0f;
        void  setFreq(float freq, float sampleRate) {
            float w = tanf(3.14159f * freq / sampleRate);
            a1      = (w - 1.0f) / (w + 1.0f);
        }
        float process(float x) {
            float y = a1 * x + z1;
            z1      = x - a1 * y;
            return y;
        }
    };

    std::vector<AllPassFilter> stages;
    float lfoPhase = 0.0f;
    float sampleRate;

public:
    float rate, depth, mix, feedback;
    float feedbackSample = 0.0f;

    Phaser(int numStages, float sampleRate, float rate = 0.5f,
           float depth = 1000.0f, float mix = 0.5f, float feedback = 0.7f)
        : stages(numStages), sampleRate(sampleRate),
          rate(rate), depth(depth), mix(mix), feedback(feedback) {}

    float process(float input) {
        float lfo = sinf(2.0f * 3.14159f * lfoPhase);
        lfoPhase += rate / sampleRate;
        if (lfoPhase >= 1.0f) lfoPhase -= 1.0f;

        float freq  = 1000.0f + lfo * depth;
        float mixed = input + feedbackSample * feedback;

        for (auto& stage : stages) {
            stage.setFreq(freq, sampleRate);
            mixed = stage.process(mixed);
        }

        feedbackSample = mixed;
        return input * (1.0f - mix) + mixed * mix;
    }
};

// Phaser using cascaded all-pass filters modulated by LFO.
// numStages controls depth of effect (typically 4, 6, 8, or 12)."""
    },
    {
        "instruction": "How do I implement a flanger effect in C++?",
        "response": """class Flanger {
    std::vector<float> delayBuffer;
    int   writePos  = 0;
    float lfoPhase  = 0.0f;
    float sampleRate;

public:
    float rate, depth, mix, feedback;
    float feedbackSample = 0.0f;

    Flanger(float sampleRate, float rate = 0.5f, float depth = 0.003f,
            float mix = 0.5f, float feedback = 0.5f)
        : sampleRate(sampleRate), rate(rate), depth(depth),
          mix(mix), feedback(feedback),
          delayBuffer(static_cast<int>(sampleRate * 0.02f), 0.0f) {}

    float process(float input) {
        float lfo = (1.0f + sinf(2.0f * 3.14159f * lfoPhase)) * 0.5f;
        lfoPhase += rate / sampleRate;
        if (lfoPhase >= 1.0f) lfoPhase -= 1.0f;

        float delaySamples = lfo * depth * sampleRate;
        int   delayInt     = static_cast<int>(delaySamples);
        float frac         = delaySamples - delayInt;

        int readA   = (writePos - delayInt + delayBuffer.size()) % delayBuffer.size();
        int readB   = (readA - 1 + delayBuffer.size()) % delayBuffer.size();
        float delayed = delayBuffer[readA] * (1.0f - frac) + delayBuffer[readB] * frac;

        delayBuffer[writePos] = input + delayed * feedback;
        writePos = (writePos + 1) % delayBuffer.size();

        return input * (1.0f - mix) + delayed * mix;
    }
};

// Flanger using LFO-modulated short delay with feedback.
// Similar to chorus but with much shorter delay times (1-10ms)."""
    },
    {
        "instruction": "How do I process audio samples in a buffer in C++?",
        "response": """// Process a mono audio buffer in-place
void processMonoBuffer(float* buffer, int numSamples, float gain) {
    for (int i = 0; i < numSamples; ++i)
        buffer[i] *= gain;
}

// Process stereo interleaved buffer (L R L R ...)
void processStereoInterleaved(float* buffer, int numFrames, float gainL, float gainR) {
    for (int i = 0; i < numFrames; ++i) {
        buffer[i * 2]     *= gainL;  // Left channel
        buffer[i * 2 + 1] *= gainR;  // Right channel
    }
}

// Mix two mono buffers together
void mixBuffers(const float* src, float* dst, int numSamples, float mix = 0.5f) {
    for (int i = 0; i < numSamples; ++i)
        dst[i] = dst[i] * (1.0f - mix) + src[i] * mix;
}

// Clear (zero) an audio buffer
void clearBuffer(float* buffer, int numSamples) {
    memset(buffer, 0, numSamples * sizeof(float));
}

// Copy one buffer to another
void copyBuffer(const float* src, float* dst, int numSamples) {
    memcpy(dst, src, numSamples * sizeof(float));
}

// Useful utilities for audio buffer manipulation in DSP processing chains."""
    },
    {
        "instruction": "How do I implement noise shaping in C++?",
        "response": """class NoiseShaper {
    float error  = 0.0f;
    float error1 = 0.0f;
    float error2 = 0.0f;

public:
    // First-order noise shaping (pushes quantization noise up in frequency)
    float processFirstOrder(float input, int bits) {
        float quantStep = 2.0f / (float)(1 << bits);
        float shaped    = input + error;
        float quantized = roundf(shaped / quantStep) * quantStep;
        error           = shaped - quantized;
        return quantized;
    }

    // Second-order noise shaping (steeper high-frequency noise push)
    float processSecondOrder(float input, int bits) {
        float quantStep = 2.0f / (float)(1 << bits);
        float shaped    = input + 2.0f * error1 - error2;
        float quantized = roundf(shaped / quantStep) * quantStep;
        error2          = error1;
        error1          = shaped - quantized;
        return quantized;
    }
};

// Noise shaping reduces perceived quantization noise by pushing it
// to higher frequencies where hearing is less sensitive.
// Use when reducing bit depth (e.g. 32-bit float to 16-bit int)."""
    },
    {
        "instruction": "How do I implement a ring modulator in C++?",
        "response": """class RingModulator {
    float carrierPhase = 0.0f;
    float sampleRate;

public:
    float carrierFreq, mix;

    RingModulator(float sampleRate, float carrierFreq = 440.0f, float mix = 1.0f)
        : sampleRate(sampleRate), carrierFreq(carrierFreq), mix(mix) {}

    void setCarrierFrequency(float freq) {
        carrierFreq = freq;
    }

    float process(float input) {
        float carrier = sinf(2.0f * 3.14159f * carrierPhase);
        carrierPhase += carrierFreq / sampleRate;
        if (carrierPhase >= 1.0f) carrierPhase -= 1.0f;

        float modulated = input * carrier;
        return input * (1.0f - mix) + modulated * mix;
    }
};

// Ring modulator multiplies input by a carrier sine wave.
// Creates sum and difference frequencies — produces metallic, bell-like tones.
// Carrier frequency controls the pitch of the effect."""
    },
    {
        "instruction": "How do I implement a tremolo effect in C++?",
        "response": """class Tremolo {
    float lfoPhase = 0.0f;
    float sampleRate;

public:
    float rate, depth;
    enum Shape { SINE, TRIANGLE, SQUARE } shape = SINE;

    Tremolo(float sampleRate, float rate = 5.0f, float depth = 0.5f)
        : sampleRate(sampleRate), rate(rate), depth(depth) {}

    float process(float input) {
        float lfo = 0.0f;

        switch (shape) {
            case SINE:
                lfo = sinf(2.0f * 3.14159f * lfoPhase);
                break;
            case TRIANGLE:
                lfo = 1.0f - 4.0f * fabsf(lfoPhase - 0.5f);
                break;
            case SQUARE:
                lfo = lfoPhase < 0.5f ? 1.0f : -1.0f;
                break;
        }

        lfoPhase += rate / sampleRate;
        if (lfoPhase >= 1.0f) lfoPhase -= 1.0f;

        float gainMod = 1.0f - depth * (lfo * 0.5f + 0.5f);
        return input * gainMod;
    }
};

// Tremolo modulates amplitude with an LFO.
// rate in Hz, depth 0.0-1.0 controls modulation amount."""
    },
    {
        "instruction": "How do I implement a simple FFT-based spectrum analyzer in C++?",
        "response": """#include <complex>
#include <vector>
#include <cmath>

class SpectrumAnalyzer {
    int fftSize;
    std::vector<float> window;

public:
    SpectrumAnalyzer(int fftSize) : fftSize(fftSize), window(fftSize) {
        // Hanning window
        for (int i = 0; i < fftSize; ++i)
            window[i] = 0.5f * (1.0f - cosf(2.0f * 3.14159f * i / (fftSize - 1)));
    }

    // Cooley-Tukey FFT (in-place, power of 2 size)
    void fft(std::vector<std::complex<float>>& data) {
        int n = data.size();
        for (int i = 1, j = 0; i < n; ++i) {
            int bit = n >> 1;
            for (; j & bit; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) std::swap(data[i], data[j]);
        }
        for (int len = 2; len <= n; len <<= 1) {
            float ang = -2.0f * 3.14159f / len;
            std::complex<float> wlen(cosf(ang), sinf(ang));
            for (int i = 0; i < n; i += len) {
                std::complex<float> w(1.0f, 0.0f);
                for (int j = 0; j < len / 2; ++j) {
                    auto u = data[i + j], v = data[i + j + len/2] * w;
                    data[i + j]          = u + v;
                    data[i + j + len/2]  = u - v;
                    w *= wlen;
                }
            }
        }
    }

    std::vector<float> getMagnitudes(const float* input) {
        std::vector<std::complex<float>> data(fftSize);
        for (int i = 0; i < fftSize; ++i)
            data[i] = input[i] * window[i];
        fft(data);
        std::vector<float> magnitudes(fftSize / 2);
        for (int i = 0; i < fftSize / 2; ++i)
            magnitudes[i] = 20.0f * log10f(std::abs(data[i]) / fftSize + 1e-9f);
        return magnitudes;
    }
};

// FFT spectrum analyzer with Hanning window and magnitude in dB.
// fftSize must be power of 2 (e.g. 512, 1024, 2048)."""
    },
    {
        "instruction": "How do I implement a DC offset removal filter in C++?",
        "response": """class DCBlocker {
    float prevInput  = 0.0f;
    float prevOutput = 0.0f;
    float coefficient;

public:
    // coefficient close to 1.0 gives lower cutoff frequency
    // Typical value: 0.995 at 44100 Hz gives ~180 Hz cutoff
    DCBlocker(float coefficient = 0.995f) : coefficient(coefficient) {}

    float process(float input) {
        float output = input - prevInput + coefficient * prevOutput;
        prevInput    = input;
        prevOutput   = output;
        return output;
    }

    void processBuffer(float* buffer, int numSamples) {
        for (int i = 0; i < numSamples; ++i)
            buffer[i] = process(buffer[i]);
    }

    // Set cutoff frequency in Hz
    void setCutoff(float cutoffHz, float sampleRate) {
        coefficient = 1.0f - (2.0f * 3.14159f * cutoffHz / sampleRate);
        coefficient = std::clamp(coefficient, 0.0f, 1.0f);
    }
};

// First-order high-pass DC blocking filter.
// Essential for removing DC offset before further DSP processing.
// Higher coefficient = lower cutoff frequency."""
    },
];


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for pair in PAIRS:
            f.write(json.dumps(pair) + "\n")
    print(f" Saved {len(PAIRS)} handcrafted pairs to:\n  {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
