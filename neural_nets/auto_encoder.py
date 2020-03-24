from keras.layers import Input, Dense
from keras.models import Model
from keras.models import load_model
from dataset_tools.encode_dataset import encode_image_with_0, encode_image_with_1
import numpy as np
import os


########################################################################################################################

def auto_encoder(x_train, y_train, x_test, y_test, clearance_level):
    if os.path.exists('/home/yonatan/PycharmProjects/Deep-Steg/models/auto_encoder_' + str(clearance_level) + '.h5'):
        print('retraining models')
        AutoEncoder = load_model('/home/yonatan/PycharmProjects/Deep-Steg/models/auto_encoder_' + str(clearance_level) + '.h5')
        Encoder = load_model('/home/yonatan/PycharmProjects/Deep-Steg/models/encoder_' + str(clearance_level) + '.h5')
        Decoder = load_model('/home/yonatan/PycharmProjects/Deep-Steg/models/decoder_' + str(clearance_level) + '.h5')
    else:
        encoding_dim = 32
        input_img = Input(shape=(784,))
        encoded = Dense(encoding_dim * 4, activation='relu')(input_img)
        encoded = Dense(encoding_dim * 2, activation='relu')(encoded)
        encoded = Dense(encoding_dim, activation='relu')(encoded)
        decoded = Dense(encoding_dim * 2, activation='relu')(encoded)
        decoded = Dense(encoding_dim * 4, activation='relu')(decoded)
        decoded = Dense(784, activation='sigmoid')(decoded)
        # model that maps the input to the reconstruction
        AutoEncoder = Model(input_img, decoded)
        # model that maps the input to the encoding
        Encoder = Model(input_img, encoded)
        encoded_input = Input(shape=(encoding_dim,))
        decoder_layer1 = AutoEncoder.layers[-3]
        decoder_layer2 = AutoEncoder.layers[-2]
        decoder_layer3 = AutoEncoder.layers[-1]
        # model that maps the encoding to the reconstruction
        Decoder = Model(encoded_input, decoder_layer3(decoder_layer2(decoder_layer1(encoded_input))))
        AutoEncoder.compile(optimizer='adadelta', loss='binary_crossentropy', metrics=['accuracy'])

    # normalize all values between 0 and 1 and flatten the 28x28 images into vectors of size 784
    x_train = x_train.astype('float32') / 255
    x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
    x_test = x_test.astype('float32') / 255
    x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))

    y_train = y_train.astype('float32') / 255
    y_train = y_train.reshape((len(y_train), np.prod(y_train.shape[1:])))
    y_test = y_test.astype('float32') / 255
    y_test = y_test.reshape((len(y_test), np.prod(y_test.shape[1:])))

    AutoEncoder.fit(x_train, y_train, batch_size=256, epochs=100, verbose=1, shuffle=True,
                    validation_data=(x_test, y_test))

    AutoEncoder.save('/home/yonatan/PycharmProjects/Deep-Steg/models/auto_encoder_' + str(clearance_level) + '.h5')
    Encoder.save('/home/yonatan/PycharmProjects/Deep-Steg/models/encoder_' + str(clearance_level) + '.h5')
    Decoder.save('/home/yonatan/PycharmProjects/Deep-Steg/models/decoder_' + str(clearance_level) + '.h5')

    print(AutoEncoder.evaluate(x_test, y_test))

    encoded_train_images = Encoder.predict(x_train)
    encoded_test_images = Encoder.predict(x_test)

    decoded_train_images = Decoder.predict(encoded_train_images)
    decoded_test_images = Decoder.predict(encoded_test_images)

    # reshape (784 => 28x28) and re-normalize
    decoded_train_images = decoded_train_images.reshape(decoded_train_images.shape[0], 28, 28)
    decoded_train_images *= 255
    decoded_train_images = decoded_train_images.astype('uint8')
    decoded_test_images = decoded_test_images.reshape(decoded_test_images.shape[0], 28, 28)
    decoded_test_images *= 255
    decoded_test_images = decoded_test_images.astype('uint8')

    return decoded_train_images, decoded_test_images


def auto_encode(image, clearance_level):
    Encoder = load_model('/home/yonatan/PycharmProjects/Deep-Steg/models/encoder_' + str(clearance_level) + '.h5')
    Decoder = load_model('/home/yonatan/PycharmProjects/Deep-Steg/models/decoder_' + str(clearance_level) + '.h5')

    encoded_image = encode_image_with_0(image) if clearance_level == 0 else encode_image_with_1(image)
    encoded_image = (encoded_image.astype('float32') / 255).reshape(1, 784)

    encoded_image = Encoder.predict(encoded_image)
    auto_encoded_image = Decoder.predict(encoded_image)

    auto_encoded_image = (auto_encoded_image * 255).astype('uint8').reshape(28, 28)

    return auto_encoded_image

########################################################################################################################