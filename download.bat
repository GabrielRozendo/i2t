E:
cd E:\Instagram

instaloader --login GabrielRozendo --stories --highlights --tagged --igtv --fast-update --geotags --no-compress-json --quiet gabrielrozendo>>eu.log

instaloader --login GabrielRozendo --stories --highlights --tagged --igtv --fast-update --geotags --no-compress-json --no-metadata-json --no-video-thumbnails --quiet --post-filter="date_utc >= datetime(2020, 11, 1)" patsilvaribeiro>>pat.log

instaloader --login GabrielRozendo --stories --highlights --igtv --fast-update --no-profile-pic --no-compress-json --no-metadata-json --no-video-thumbnails --quiet --post-filter="date_utc >= datetime(2020, 11, 1)" cocatechpod>>cocatech.log
