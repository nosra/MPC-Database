from django.db import migrations

def seed_categories(apps, schema_editor):
    Category = apps.get_model('home', 'Category')
    Subcategory = apps.get_model('home', 'Subcategory')

    data = {
        "Effects": [
            ("Reverb", "reverb"),
            ("Delay", "delay"),
            ("Chorus", "chorus"),
            ("Flanger", "flanger"),
            ("Phaser", "phaser"),
            ("Distortion", "distortion"),
            ("Saturation", "saturation"),
            ("Bitcrusher", "bitcrusher"),
            ("Tremolo", "tremolo"),
            ("Stereo Imaging", "stereo"),
        ],
        "Dynamics": [
            ("Compressor", "compressor"),
            ("Limiter", "limiter"),
            ("Gate", "gate"),
            ("Transient Shaper", "transient"),
            ("De-esser", "deesser"),
            ("Multiband Compressor", "multiband"),
        ],
        "EQ & Filtering": [
            ("Parametric EQ", "peq"),
            ("Graphic EQ", "geq"),
            ("Dynamic EQ", "deq"),
            ("High/Low Pass Filter", "filters"),
            ("Resonant Filter", "resfilter"),
        ],
        "Synthesizers": [
            ("Analog Modeling", "analog"),
            ("FM Synth", "fm"),
            ("Wavetable", "wavetable"),
            ("Granular", "granular"),
            ("Additive", "additive"),
            ("Subtractive", "subtractive"),
            ("Modular", "modular"),
        ],
        "Sampling": [
            ("Sampler", "sampler"),
            ("Drum Sampler", "drumsampler"),
            ("Loop Player", "loopplayer"),
            ("Rompler", "rompler"),
        ],
        "Utilities": [
            ("Spectrum Analyzer", "analyzer"),
            ("Metering", "metering"),
            ("Tuner", "tuner"),
            ("MIDI Utility", "midiutil"),
            ("Gain/Volume", "gain"),
            ("Phase Alignment", "phase"),
        ],
        "Pitch & Time": [
            ("Pitch Correction", "pitchcorr"),
            ("Pitch Shifter", "pitchshift"),
            ("Time Stretching", "timestretch"),
            ("Harmonizer", "harmonizer"),
        ],
        "Creative FX": [
            ("Glitch", "glitch"),
            ("Reverse", "reverse"),
            ("Looper", "looper"),
            ("Granular FX", "granfx"),
            ("Stutter", "stutter"),
        ],
        "Mastering": [
            ("Mastering Suite", "mastersuite"),
            ("Exciter", "exciter"),
            ("Stereo Enhancer", "stereoenh"),
            ("Loudness Meter", "loudmeter"),
        ],
        "Instruments": [
            ("Piano", "piano"),
            ("Strings", "strings"),
            ("Brass", "brass"),
            ("Guitar", "guitar"),
            ("Bass", "bass"),
            ("Drums", "drums"),
            ("Orchestral", "orchestral"),
        ],
    }

    for cat_name, subs in data.items():
        category, _ = Category.objects.get_or_create(
            name=cat_name,
            slug=cat_name.lower().replace(" ", "")[:10]
        )

        for sub_name, slug in subs:
            Subcategory.objects.get_or_create(
                parent=category,
                name=sub_name,
                slug=slug
            )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('yourappname', 'Category')
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_alternativeplugin_subcategory_proplugin_subcategory'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]

