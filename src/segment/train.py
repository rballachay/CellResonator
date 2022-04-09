import click
from src.segment.dataset import augment_dataset, load_dataset, split_dataset
from src.segment.model import build_unet
from src.segment.utils import jaccard_index
from tensorflow.keras.callbacks import CSVLogger, ModelCheckpoint


@click.command()
@click.option(
    "-i",
    "image_path",
    prompt=False,
    help="Path to images",
)
@click.option(
    "-m",
    "mask_path",
    prompt=False,
    help="Path to masks",
)
@click.option(
    "-o",
    "log_path",
    prompt=False,
    help="Path to log files and model",
)
def main(image_path: str, mask_path: str, log_path: str):
    dataset_0 = load_dataset(image_path, mask_path)
    dataset = augment_dataset(dataset_0)

    X_train, Y_train, X_test, Y_test = split_dataset(dataset)

    model = build_unet(img_shape=X_train.shape[1:])
    model.summary()

    checkpoint = ModelCheckpoint(
        f"{log_path}/checkpount.txt",
        monitor="val_accuracy",
        verbose=1,
        save_best_only=True,
        mode="max",
    )
    csv_logger = CSVLogger(f"{log_path}/csv_logger.txt", separator=",", append=False)
    callbacks_list = [checkpoint, csv_logger]  # early_stopping

    # compile model
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", jaccard_index],
    )

    # train and save model
    model.fit(
        X_train,
        Y_train,
        epochs=5,
        batch_size=8,
        validation_data=(X_test, Y_test),
        callbacks=callbacks_list,
        verbose=1,
    )
    model.save(log_path)
    print("model saved:", log_path)


if __name__ == "__main__":
    main()
