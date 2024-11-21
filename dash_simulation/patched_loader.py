from dask import dataframe as dd
from mtpy.loaders.aconity import AconityLoader
from read_aconity_layers import read_layer


class PatchedAconityLoader(AconityLoader):
    def stream_layer(self, filename):
        data = read_layer(filename)
        layer_dir, storage_options = self.array_to_parquet(data)
        ddf = dd.read_parquet(
            self.fs.unstrip_protocol(layer_dir),
            storage_options=storage_options,
            parquet_file_extension=".parquet",
        )
        self.data = dd.concat([self.data, ddf])
        return ddf

    def array_to_parquet(self, data):
        ddf = dd.from_array(
            data,
            columns=["x", "y", "z", "t", "rgb"],
        ).drop("rgb", axis=1)  # The 'RGB' column is superfluous, as far as i can tell.
        storage_options = getattr(self.fs, "storage_options", {})
        target_options = storage_options.get("target_options", storage_options)
        live_cache = f"{self._data_cache}live/"
        self.fs.mkdirs(live_cache, exist_ok=True)
        current_layer = f"{live_cache}{self.next_layer()}"
        ddf = ddf.repartition(partition_size="100MB")
        ddf.to_parquet(
            self.fs.unstrip_protocol(current_layer),
            storage_options=target_options,
            compression="lz4",
            append=True,
            compute=True,
            write_metadata_file=True,
            ignore_divisions=True,
        )
        return current_layer, storage_options

    def next_layer(self):
        self._i = getattr(self, "_i", -1) + 1
        return self._i
