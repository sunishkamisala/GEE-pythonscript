import ee
ee.Initialize()

########## VARS TO DEFINE ####################################################
##############################################################################

# this string will appear in EE and help you remember what is running
# be short but descriptive
description = 'silos_in_ia'

# where do the point geometries of the silos live? Mutlu should be able
# to share link
paht_to_points = 'users/benthompson/silopointstest'

# what size chips do you want? chips will be KERNEL_SIZE x KERNEL_SIZE
KERNEL_SIZE = 256

# which bands of the image do you want to use
BANDS = ['R','G','B','N']

# what is the name of the bucket and folder in bucket you will be exporting to
# this is for exporting to cloud, if you're exporting to your personal drive
# lines 49 - 56 will need to be modified to ee.batch.Export.table.toDrive(...)
BUCKET = 'agyield'
FOLDER = 'path/to/save/files'

##############################################################################
#####################################LOGIC####################################
##############################################################################

# import NAIP and convert from image collection to single image
naip = (ee.ImageCollection('USDA/NAIP/DOQQ')
	.filter(ee.Filter.date('2017-01-01', '2018-12-31'))
	.select(BANDS)
	.mosaic())

# import collection of points and convert to squares
points = ee.FeatureCollection(paht_to_points)
# buffer points and make squares
points = points.map(lambda x: x.buffer(KERNEL_SIZE//2))
points = points.map(lambda x: x.bounds())
points_list = points.toList(points.size())

# iterate through points and export tiff for each one
for i in range(points_list.size().getInfo()):
	samp = naip.clip(points_list.get(i))

	task = ee.batch.Export.image.toCloudStorage(
		image = samp,
		description = '{}_{}'.format(description,i),
		bucket = BUCKET,
		fileNamePrefix = '{}/{}_{}'.format(FOLDER,description,i),
		fileFormat = 'GeoTIFF',
		region = ee.Feature(points_list.get(i)).geometry(),
		scale = 1,
		maxPixels = 1e13
		)
	task.start()