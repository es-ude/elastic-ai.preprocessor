typedef struct {
    float sampling_rate;
    int   dsr;
} SettingsDownSampling;

extern const SettingsDownSampling DefaultSettingsDownSampling;

float sampling_rate_out(const SettingsDownSampling *s);

void do_simple(
        const SettingsDownSampling *s,
        const float *uin,
        size_t in_size,
        float *uout);
