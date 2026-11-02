package com.github.sebastiandotdev.symbols

import com.intellij.openapi.vfs.VirtualFile
import javax.swing.Icon

object IconResolver {

  fun forFile(virtualFile: VirtualFile): Icon? {
    return if (virtualFile.isDirectory) forFolder(virtualFile.name) else forFileName(virtualFile.name)
  }

  fun forFolder(name: String): Icon {
    return Icons.FOLDER_TO_ICON[name.lowercase()] ?: Icons.folder
  }

  // Gradle source set modules are named "<project>.<sourceSet>", e.g. "Symbols.test"
  fun forModule(name: String): Icon {
    return forFolder(name.substringAfterLast('.'))
  }

  fun forFileName(name: String): Icon? {
    val fileName = name.lowercase()

    return Icons.FILE_TO_ICON[fileName]
      ?: findExtensionIcon(fileName)
  }

  private fun findExtensionIcon(fileName: String): Icon? {
    // We want to check for "test.tsx", "tsx" and "ts" extensions in that order.
    // 1. "test.tsx"
    // 2. "tsx"
    val parts = fileName.split(".")
    for (i in parts.indices) {
      val ext = parts.subList(i, parts.size).joinToString(".")
      Icons.EXT_TO_ICON[ext]?.let { return it }
    }
    return null
  }
}
