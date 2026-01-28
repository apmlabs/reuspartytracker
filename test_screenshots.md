# Police Detection Test Screenshots

## With Police (should detect police_cars >= 1)
- frame_20260127_170441.png - White police car with blue lights (18:04)
- frame_20260127_180627.png - Police car with blue lights bottom right (19:06)
- frame_20260127_234510.png - Blue flashing lights (00:45)
- frame_20260128_091346.png - Yellow/blue Policía Local + DHL van (should be 1 police, not 2) (10:13)
- frame_20260128_093346.png - Yellow/blue Policía Local, partially hidden (10:33)
- frame_20260128_094846.png - Yellow/blue Policía Local, clear view (10:48)
- frame_20260128_100650.png - Yellow/blue Policía Local (11:06)
- frame_20260128_102321.png - Yellow/blue Policía Local, partially hidden by white van (11:23)
- frame_20260128_103321.png - Yellow/blue Policía Local (11:33)
- frame_20260128_104352.png - Yellow/blue Policía Local (11:43)

## Without Police (should detect police_cars = 0)
- frame_20260127_181127.png - No police
- frame_20260127_223010.png - No police
- frame_20260128_105556.png - No police, 720p quality
- frame_20260128_132639.png - No police (false positive test - AI mis-detected)
- frame_20260128_133649.png - No police (false positive - AI detected police_score=2)
- frame_20260128_133751.png - No police (false positive - AI detected police_score=4)
