package com.labnotescan

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.work.Data
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager

class MainActivity : ComponentActivity() {
    private var selectedInputUri: Uri? = null
    private var selectedOutputTree: Uri? = null

    private val pickInput = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) selectedInputUri = uri
    }

    private val pickOutputTree = registerForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri != null) selectedOutputTree = uri
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        findViewById<android.view.View>(R.id.pickInputButton).setOnClickListener {
            pickInput.launch(arrayOf("image/*", "application/pdf", "application/zip"))
        }

        findViewById<android.view.View>(R.id.pickOutputButton).setOnClickListener {
            pickOutputTree.launch(null)
        }

        findViewById<android.view.View>(R.id.convertButton).setOnClickListener {
            enqueueConversion()
        }
    }

    private fun enqueueConversion() {
        val input = selectedInputUri ?: return
        val output = selectedOutputTree ?: return
        val data = Data.Builder()
            .putString("inputUri", input.toString())
            .putString("outputTreeUri", output.toString())
            .putString("ocrLanguage", "eng")
            .putInt("ocrDpi", 300)
            .putString("ocrPreprocessing", "none")
            .build()

        val request = OneTimeWorkRequestBuilder<ConversionWorker>()
            .setInputData(data)
            .build()
        WorkManager.getInstance(this).enqueue(request)
    }
}
