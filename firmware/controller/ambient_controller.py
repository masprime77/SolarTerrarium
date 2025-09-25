import random
import config
import time
from drivers.led_neopixel import LedNeopixel
from utils.scale_rgb import scale_rgb

class AmbientController:
    def __init__(self, led: LedNeopixel, fps: int = 24):
        self._led = led
        self._default_brightness = led.brightness
        self._fps = fps
        self._f_duration_ms = int(1000 / fps)

        now = time.ticks_ms()
        self._last_frame_ms = now

        self._t_cloud_step = now
        self._cloud_pos = 0
        self._cloudy_stars_map = self._generate_objects(10)
        self._clear_night_map = self._generate_objects(4)

    def _generate_objects(self, qty_objects):
        objects_idx = []
        objects_map = []
        for _ in range(qty_objects):
            random_object = random.randint(0, self._led.pixel_count() - 1)
            while random_object in objects_idx:
                random_object = random.randint(0, self._led.pixel_count() - 1)
            objects_idx.append(random_object)

        for led in range(self._led.pixel_count()):
            is_object = False
            for obj in objects_idx:
                if led == obj:
                    is_object = True
                    break
            objects_map.append(is_object)

        return objects_map
    
    def _blinking_map(self, step, objects_map, breathe_duration_ms,
                      breathe_pause_ms, pause_between_ms, color_base,
                      color_object):
        for i in range(2, step + 2):
            c = scale_rgb(color_object, i * (1.0 / step))
            for j in range(self._led.pixel_count()):
                if objects_map[j]:
                    self._led.set_pixel(pixel=j, color=c, show=False)
                else:
                    self._led.set_pixel(pixel=j, color=color_base, show=False)
            self._led.show()
            time.sleep_ms(breathe_duration_ms // step)

        time.sleep_ms(breathe_pause_ms)

        for i in range(step + 1, 1, -1):
            c = scale_rgb(color_object, i * (1.0 / step))
            for j in range(self._led.pixel_count()):
                if objects_map[j]:
                    self._led.set_pixel(pixel=j, color=c, show=False)
                else:
                    self._led.set_pixel(pixel=j, color=color_base, show=False)
            self._led.show()
            time.sleep_ms(breathe_duration_ms // step)

        time.sleep_ms(pause_between_ms)

    def _pat_clear_day(self):
        self._led.set_all(config.COLOR_SKY_DAY, show=True)

    def _pat_clear_night(self, stars=3):
        for i in range(self._led.pixel_count()):
            if self._clear_night_map[i]:
                self._led.set_pixel(pixel=i, color=config.COLOR_STARS,
                                    show=False)
            else:
                self._led.set_pixel(pixel=i, color=config.COLOR_SKY_NIGHT,
                                    show=False)
        
        self._led.show()

    def _pat_cloudy_day(self, visibility=0.75, cloud_passthrough=0.1,
                        cloud_size=12, cloud_speed_ms=1250):
        cloudy  = scale_rgb(config.COLOR_SKY_DAY_CLOUDY, visibility)
        now = time.ticks_ms()

        if time.ticks_diff(now, self._t_cloud_step) >= cloud_speed_ms:
            self._cloud_pos = (self._cloud_pos + 1) % (self._led.pixel_count() / 2)
            self._t_cloud_step = now

        self._led.set_all(cloudy, show=False)

        pixels = list(range(self._led.pixel_count()))
        sky1 = pixels[0:(self._led.pixel_count() // 2)]
        sky2 = pixels[(self._led.pixel_count() // 2):self._led.pixel_count()]
        sky2.reverse()
        clouded = scale_rgb(cloudy, cloud_passthrough)

        for i in range(0, (self._led.pixel_count() // 2)):
            px_distance_to_cloud_px = (i - self._cloud_pos) % (self._led.pixel_count() // 2)
            if px_distance_to_cloud_px < cloud_size:
                self._led.set_pixel(sky1[i], clouded, show=False)
                self._led.set_pixel(sky2[i], clouded, show=False)

        self._led.show()

    def _pat_cloudy_night(self, cloud_speed_ms=1250, cloud_size=12,
                          cloud_passthrough=0.1):
        now = time.ticks_ms()

        if time.ticks_diff(now, self._t_cloud_step) >= cloud_speed_ms:
            self._cloud_pos = (self._cloud_pos + 1) % (self._led.pixel_count() / 2)
            self._t_cloud_step = now

        for i in range(self._led.pixel_count()):
            if self._cloudy_stars_map[i]:
                self._led.set_pixel(pixel=i, color=config.COLOR_STARS,
                                    show=False)
            else:
                self._led.set_pixel(pixel=i, color=config.COLOR_SKY_NIGHT,
                                    show=False)

        pixels = list(range(self._led.pixel_count()))
        sky1 = pixels[0:(self._led.pixel_count() // 2)]
        sky2 = pixels[(self._led.pixel_count() // 2):self._led.pixel_count()]
        sky2.reverse()

        lights = self._led.frame().copy()

        for i in range(0, (self._led.pixel_count() // 2)):
            px_distance_to_cloud_px = (i - self._cloud_pos) % (self._led.pixel_count() // 2)
            if px_distance_to_cloud_px < cloud_size:
                self._led.set_pixel(sky1[i],
                                    scale_rgb(lights[sky1[i]],cloud_passthrough),
                                    show=False)
                self._led.set_pixel(sky2[i],
                                    scale_rgb(lights[sky2[i]], cloud_passthrough),
                                    show=False)
                
        self._led.show()

    def _pat_rain_day(self, visibility=0.3, step=5, breathe_duration_ms=15,
                      breathe_pause_ms=15, pause_between_ms=0, drops=2):
        rain_map = self._generate_objects(drops)
        rainy = scale_rgb(config.COLOR_SKY_DAY_CLOUDY, visibility)
        self._led.set_all(rainy, show=False)
        self._blinking_map(step=step, objects_map=rain_map,
                           breathe_duration_ms=breathe_duration_ms,
                           breathe_pause_ms=breathe_pause_ms, color_base=rainy,
                           pause_between_ms=pause_between_ms,
                           color_object=config.COLOR_RAIN_DAY)

    def _pat_rain_night(self, step=5, breathe_duration_ms=15,
                        breathe_pause_ms=15, pause_between_ms=0, drops=2):
        rain_map = self._generate_objects(drops)
        self._led.set_all(config.COLOR_SKY_NIGHT, show=False)
        self._blinking_map(step=step,
                           objects_map=rain_map,
                           breathe_duration_ms=breathe_duration_ms,
                           breathe_pause_ms=breathe_pause_ms,
                           pause_between_ms=pause_between_ms,
                           color_base=config.COLOR_SKY_NIGHT,
                           color_object=config.COLOR_RAIN_NIGHT)

    def _pat_snow_day(self, visibility=0.2, step=24, breathe_duration_ms=600,
                      breathe_pause_ms=250, pause_between_ms=0, snowflakes=4):
        snow_map = self._generate_objects(snowflakes)
        snowy = scale_rgb(config.COLOR_SKY_DAY_CLOUDY, visibility)
        self._led.set_all(snowy, show=False)
        self._blinking_map(step=step, objects_map=snow_map,
                           breathe_duration_ms=breathe_duration_ms,
                           breathe_pause_ms=breathe_pause_ms,
                           pause_between_ms=pause_between_ms,
                           color_base=snowy,
                           color_object=config.COLOR_SNOW_DAY)

    def _pat_snow_night(self, step=24, breathe_duration_ms=600,
                        breathe_pause_ms=250, pause_between_ms=0, snowflakes=4):
        snow_map = self._generate_objects(snowflakes)
        self._led.set_all(config.COLOR_SKY_NIGHT, show=False)
        self._blinking_map(step=step, objects_map=snow_map,
                            breathe_duration_ms=breathe_duration_ms,
                            breathe_pause_ms=breathe_pause_ms,
                            pause_between_ms=pause_between_ms,
                            color_base=config.COLOR_SKY_NIGHT,
                            color_object=config.COLOR_SNOW_NIGHT)

    def _pat_storm_day(self, visibility=0.1, step=5, breathe_duration_ms=15,
                      breathe_pause_ms=15, pause_between_ms=0, drops=2,
                      lightning_chance=0.075):
        self._pat_rain_day(visibility=visibility, step=step,
                          breathe_duration_ms=breathe_duration_ms,
                          breathe_pause_ms=breathe_pause_ms,
                          pause_between_ms=pause_between_ms, drops=drops)
        
        rainy = scale_rgb(config.COLOR_SKY_DAY_CLOUDY, visibility)
        if random.random() < lightning_chance:
            self._led.set_all(config.COLOR_LIGHTNING, show=True)
            time.sleep_ms(100)
            self._led.set_all(rainy, show=True)
            time.sleep_ms(200)
            self._led.set_all(config.COLOR_LIGHTNING, show=True)
            time.sleep_ms(50)
            self._led.set_all(rainy, show=True)

    def _pat_storm_night(self, step=5, breathe_duration_ms=15,
                        breathe_pause_ms=15, pause_between_ms=0, drops=2,
                        lightning_chance=0.075):
        self._pat_rain_night(step=step, breathe_duration_ms=breathe_duration_ms,
                             breathe_pause_ms=breathe_pause_ms,
                             pause_between_ms=pause_between_ms, drops=drops)
        
        if random.random() < lightning_chance:
            self._led.set_all(config.COLOR_LIGHTNING, show=True)
            time.sleep_ms(100)
            self._led.set_all(config.COLOR_SKY_NIGHT, show=True)
            time.sleep_ms(200)
            self._led.set_all(config.COLOR_LIGHTNING, show=True)
            time.sleep_ms(50)
            self._led.set_all(config.COLOR_SKY_NIGHT, show=True)

    def _pat_unwnown(self):
        self._led.breathe(times=1, colors=[config.COLOR_RED], step=30,
                          breathe_duration_ms=1000, end_on=False)

    def render(self, weather):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_frame_ms) < self._f_duration_ms:
            return
        self._last_frame_ms = now

        ok = weather.get("ok", False)
        wmo = weather.get("wmo", None)
        is_day = weather.get("is_day", True)
        age_s = weather.get("age_s", 0)

        if not ok or wmo is None:
            self._pat_unwnown()
        elif is_day:
            if wmo in (0, 1):
                self._pat_clear_day()
            elif wmo in (2, 3):
                self._pat_cloudy_day(visibility=0.75, cloud_passthrough=0.2,
                                     cloud_size=12, cloud_speed_ms=1250)
            elif wmo in (45, 48):
                self._pat_cloudy_day(visibility=0.4, cloud_passthrough=0.1,
                                     cloud_size=13,cloud_speed_ms=1500)
            elif wmo in (51, 53, 55, 56, 57, 80, 81):
                self._pat_rain_day(visibility=0.25, step=10,
                                   breathe_duration_ms=30, breathe_pause_ms=30,
                                   pause_between_ms=10, drops=1)
            elif wmo in (61, 63, 65, 66, 67, 82, 85, 86):
                self._pat_rain_day(visibility=0.2, step=10,
                                   breathe_duration_ms=15, breathe_pause_ms=15,
                                   pause_between_ms=0, drops=2)
            elif wmo in (71, 73):
                self._pat_snow_day(visibility=0.175, step=24,breathe_duration_ms=600,
                                   breathe_pause_ms=250, pause_between_ms=20,
                                   snowflakes=4)
            elif wmo in (75, 77):
                self._pat_snow_day(visibility=0.12, step=24,breathe_duration_ms=400,
                                   breathe_pause_ms=150, pause_between_ms=0,
                                   snowflakes=4)
            elif wmo in (95, 96, 99):
                self._pat_storm_day(visibility=0.1, step=5,
                                   breathe_duration_ms=12, breathe_pause_ms=12,
                                   pause_between_ms=0, drops=2,
                                   lightning_chance=0.075)
            else:
                self._pat_unknown()
        
        elif not is_day:
            if wmo in (0, 1):
                self._pat_clear_night()
            elif wmo in (2, 3):
                self._pat_cloudy_night(cloud_speed_ms=1250, cloud_size=12,
                                      cloud_passthrough=0.2)
            elif wmo in (45, 48):
                self._pat_cloudy_night(cloud_speed_ms=1500, cloud_size=13,
                                      cloud_passthrough=0.1)
            elif wmo in (51, 53, 55, 56, 57, 80, 81):
                self._pat_rain_night(step=10, breathe_duration_ms=30,
                                    breathe_pause_ms=30, pause_between_ms=10, drops=1)
            elif wmo in (61, 63, 65, 66, 67, 82, 85, 86):
                self._pat_rain_night(step=10, breathe_duration_ms=15,breathe_pause_ms=15,
                                    pause_between_ms=0, drops=2)
            elif wmo in (71, 73):
                self._pat_snow_night(step=24, breathe_duration_ms=600,
                                    breathe_pause_ms=250, pause_between_ms=20,
                                    snowflakes=4)
            elif wmo in (75, 77):
                self._pat_snow_night(step=24, breathe_duration_ms=400,
                                     breathe_pause_ms=150, pause_between_ms=0,
                                     snowflakes=4)
            elif wmo in (95, 96, 99):
                self._pat_storm_night(step=5, breathe_duration_ms=12,
                                     breathe_pause_ms=12, pause_between_ms=0, drops=2,
                                     lightning_chance=0.075)
            else:
                self._pat_unknown()
        
        else:
            self._pat_unknown()