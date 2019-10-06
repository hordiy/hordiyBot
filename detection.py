import face_recognition
from PIL import Image, ImageDraw
import numpy as np

def face_recong(down_file):
	# Load a sample picture and learn how to recognize it.
	me_image = face_recognition.load_image_file("me.jpg")
	me_face_encoding = face_recognition.face_encodings(me_image)[0]

	mick_image = face_recognition.load_image_file("mick.jpg")
	mick_face_encoding = face_recognition.face_encodings(mick_image)[0]

	nik_image = face_recognition.load_image_file("nik.jpg")
	nik_face_encoding = face_recognition.face_encodings(nik_image)[0]

	max_image = face_recognition.load_image_file("max.jpg")
	max_face_encoding = face_recognition.face_encodings(max_image)[0]

	yulia_image = face_recognition.load_image_file("yulia.jpg")
	yulia_face_encoding = face_recognition.face_encodings(yulia_image)[0]

	known_face_encodings = [
	    me_face_encoding,
	    mick_face_encoding,
	    nik_face_encoding,
	    max_face_encoding,
	    yulia_face_encoding
	]
	known_face_names = [
	    "Vlad",
	    "Michael",
	    "Nikolai",
	    "Max",
	    "Yulia"
	]

	unknown_image = face_recognition.load_image_file(down_file)

	face_locations = face_recognition.face_locations(unknown_image)
	face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

	pil_image = Image.fromarray(unknown_image)
	draw = ImageDraw.Draw(pil_image)

	for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
	    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

	    name = "Unknown"

	    # If a match was found in known_face_encodings, just use the first one.
	    # if True in matches:
	    #     first_match_index = matches.index(True)
	    #     name = known_face_names[first_match_index]

	    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
	    best_match_index = np.argmin(face_distances)
	    if matches[best_match_index]:
	        name = known_face_names[best_match_index]

	    draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

	    text_width, text_height = draw.textsize(name)
	    draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
	    draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

	del draw

	# Display the resulting image
	#pil_image.show()

	pil_image.save("image_with_boxes.jpg")