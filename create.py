# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(".")
FILES = {}

FILES["settings.gradle.kts"] = '''pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "VideoEditor"
include(":app")
'''

FILES["build.gradle.kts"] = '''plugins {
    id("com.android.application") version "8.2.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}
'''

FILES["gradle.properties"] = '''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
'''

FILES[".gitignore"] = '''.gradle/
build/
local.properties
.idea/
*.iml
*.apk
'''

FILES["app/build.gradle.kts"] = '''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.videoeditor"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.videoeditor"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildFeatures { compose = true }
    composeOptions { kotlinCompilerExtensionVersion = "1.5.8" }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    
    implementation("androidx.media3:media3-transformer:1.3.1")
    implementation("androidx.media3:media3-effect:1.3.1")
    implementation("androidx.media3:media3-common:1.3.1")
    implementation("androidx.media3:media3-exoplayer:1.3.1")
    implementation("androidx.media3:media3-ui:1.3.1")
}
'''

FILES["app/src/main/AndroidManifest.xml"] = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />

    <application
        android:label="مونتاج بسيط"
        android:icon="@android:drawable/ic_media_play"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''

FILES["app/src/main/java/com/example/videoeditor/MainActivity.kt"] = '''package com.example.videoeditor

import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.media3.common.MediaItem
import androidx.media3.transformer.Composition
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.Transformer
import java.io.File

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                VideoEditorScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VideoEditorScreen() {
    val context = LocalContext.current
    
    var videoUri by remember { mutableStateOf<Uri?>(null) }
    var audioUri by remember { mutableStateOf<Uri?>(null) }
    
    var startTime by remember { mutableStateOf("0") }
    var endTime by remember { mutableStateOf("10") }
    var speed by remember { mutableStateOf("1.0") }
    
    var isExporting by remember { mutableStateOf(false) }

    val pickVideo = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) videoUri = uri
    }

    val pickAudio = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) audioUri = uri
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("تطبيق المونتاج البسيط", style = MaterialTheme.typography.headlineSmall)
        
        Button(onClick = { pickVideo.launch(arrayOf("video/*")) }, modifier = Modifier.fillMaxWidth()) {
            Text(if (videoUri == null) "1. اختر الفيديو" else "✅ تم اختيار الفيديو")
        }

        Button(onClick = { pickAudio.launch(arrayOf("audio/*")) }, modifier = Modifier.fillMaxWidth()) {
            Text(if (audioUri == null) "2. اختر الصوت (اختياري)" else "✅ تم اختيار الصوت")
        }

        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            OutlinedTextField(
                value = startTime,
                onValueChange = { startTime = it },
                label = { Text("البداية (ثانية)") },
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.width(8.dp))
            OutlinedTextField(
                value = endTime,
                onValueChange = { endTime = it },
                label = { Text("النهاية (ثانية)") },
                modifier = Modifier.weight(1f)
            )
        }

        OutlinedTextField(
            value = speed,
            onValueChange = { speed = it },
            label = { Text("السرعة (مثلاً 1.0 عادي، 2.0 تسريع)") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (isExporting) {
            CircularProgressIndicator()
            Text("جاري معالجة الفيديو... انتظر")
        } else {
            Button(
                onClick = {
                    if (videoUri == null) {
                        Toast.makeText(context, "الرجاء اختيار فيديو أولاً", Toast.LENGTH_SHORT).show()
                        return@Button
                    }
                    isExporting = true
                    exportVideo(context, videoUri!!, audioUri, startTime, endTime, speed) { success, msg ->
                        isExporting = false
                        Toast.makeText(context, msg, Toast.LENGTH_LONG).show()
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp)
            ) {
                Text("▶ تصدير الفيديو")
            }
        }
    }
}

fun exportVideo(
    context: android.content.Context,
    videoUri: Uri,
    audioUri: Uri?,
    startTimeStr: String,
    endTimeStr: String,
    speedStr: String,
    onResult: (Boolean, String) -> Unit
) {
    try {
        val startMs = ((startTimeStr.toDoubleOrNull() ?: 0.0) * 1000).toLong()
        val endMs = ((endTimeStr.toDoubleOrNull() ?: 10.0) * 1000).toLong()
        val speedVal = speedStr.toFloatOrNull() ?: 1.0f

        val outputFile = File(context.getExternalFilesDir(Environment.DIRECTORY_MOVIES), "edited_${System.currentTimeMillis()}.mp4")

        val videoItem = MediaItem.Builder()
            .setUri(videoUri)
            .setClippingConfiguration(
                MediaItem.ClippingConfiguration.Builder()
                    .setStartPositionMs(startMs)
                    .setEndPositionMs(endMs)
                    .build()
            )
            .build()

        val editedVideo = EditedMediaItem.Builder(videoItem)
            .setSpeed(speedVal)
            .build()

        val mediaList = mutableListOf(editedVideo)
        if (audioUri != null) {
            val audioItem = MediaItem.fromUri(audioUri)
            val editedAudio = EditedMediaItem.Builder(audioItem).build()
            mediaList.add(editedAudio)
        }

        val composition = Composition.Builder(mediaList).build()

        val transformer = Transformer.Builder(context)
            .addListener(object : Transformer.Listener {
                override fun onCompleted(composition: Composition, exportResult: androidx.media3.transformer.ExportResult) {
                    onResult(true, "✅ تم الحفظ بنجاح في مجلد الأفلام (Movies)")
                }

                override fun onError(composition: Composition, exportResult: androidx.media3.transformer.ExportResult, exportException: androidx.media3.transformer.ExportException) {
                    onResult(false, "❌ خطأ: ${exportException.message}")
                }
            })
            .build()

        transformer.start(composition, outputFile.absolutePath)
        
    } catch (e: Exception) {
        onResult(false, "خطأ غير متوقع: ${e.message}")
    }
}
'''

for rel, content in FILES.items():
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
print("Done creating files!")
