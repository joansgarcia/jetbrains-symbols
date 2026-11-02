package com.github.sebastiandotdev.symbols

import com.intellij.ide.IconProvider
import com.intellij.psi.PsiElement
import com.intellij.psi.util.PsiUtilCore
import javax.swing.Icon

class IconProvider : IconProvider() {

  override fun getIcon(element: PsiElement, flags: Int): Icon? {
    val virtualFile = PsiUtilCore.getVirtualFile(element) ?: return null

    return IconResolver.forFile(virtualFile)
  }
}
