package com.labnotescan

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

class ConversionWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    override suspend fun doWork(): Result {
        val inputUri = inputData.getString("inputUri") ?: return Result.failure()
        val outputTreeUri = inputData.getString("outputTreeUri") ?: return Result.failure()

        // Placeholder bridge:
        // 1) Read SAF inputUri into app cache file
        // 2) Invoke shared conversion API: convert(input_uri, output_dir, options)
        // 3) Copy resulting markdown files into outputTreeUri via DocumentFile
        val _ = inputUri to outputTreeUri

        return Result.success()
    }
}
