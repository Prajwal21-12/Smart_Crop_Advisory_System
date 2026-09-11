import os
import json
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2

# ==============================
# PATHS
# ==============================

TRAIN_DIR = r"C:\Users\harih\Downloads\archive (1)\PlantVillage\train"
VAL_DIR = r"C:\Users\harih\Downloads\archive (1)\PlantVillage\val"

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "plant_disease_model.keras")
CLASS_PATH = os.path.join(MODEL_DIR, "plant_disease_classes.json")

os.makedirs(MODEL_DIR, exist_ok=True)

# ==============================
# SETTINGS
# ==============================

IMG_SIZE = (160, 160)
BATCH_SIZE = 32
EPOCHS = 5
SEED = 123

# ==============================
# LOAD DATASET
# ==============================

print("\nLoading training dataset...")

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

print("\nLoading validation dataset...")

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = train_ds.class_names
NUM_CLASSES = len(class_names)

print("\n================================")
print("Number of classes:", NUM_CLASSES)
print("================================")

print("\nClasses:")
for i, name in enumerate(class_names):
    print(i, ":", name)

# Save class names for Flask later
with open(CLASS_PATH, "w", encoding="utf-8") as f:
    json.dump(class_names, f, indent=2)

# ==============================
# PERFORMANCE
# ==============================

AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.prefetch(AUTOTUNE)
val_ds = val_ds.prefetch(AUTOTUNE)

# ==============================
# DATA AUGMENTATION
# ==============================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# ==============================
# MOBILE NET V2
# ==============================

base_model = MobileNetV2(
    input_shape=(160, 160, 3),
    include_top=False,
    weights="imagenet"
)

# Freeze pretrained layers
base_model.trainable = False

# ==============================
# BUILD MODEL
# ==============================

inputs = layers.Input(shape=(160, 160, 3))

x = data_augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(0.2)(x)

outputs = layers.Dense(
    NUM_CLASSES,
    activation="softmax"
)(x)

model = models.Model(inputs, outputs)

# ==============================
# COMPILE
# ==============================

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==============================
# TRAIN
# ==============================

print("\n================================")
print("STARTING PLANT DISEASE TRAINING")
print("================================\n")

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# ==============================
# SAVE MODEL
# ==============================

model.save(MODEL_PATH)

print("\n================================")
print("TRAINING COMPLETE!")
print("================================")

print("Model saved to:")
print(MODEL_PATH)

print("\nClasses saved to:")
print(CLASS_PATH)

print("\nFinal training accuracy:",
      history.history["accuracy"][-1])

print("Final validation accuracy:",
      history.history["val_accuracy"][-1])