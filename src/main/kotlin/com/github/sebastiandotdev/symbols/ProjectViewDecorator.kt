package com.github.sebastiandotdev.symbols

import com.intellij.ide.projectView.PresentationData
import com.intellij.ide.projectView.ProjectViewNode
import com.intellij.ide.projectView.ProjectViewNodeDecorator
import com.intellij.ide.projectView.impl.ModuleGroup
import com.intellij.openapi.module.Module
import com.intellij.psi.PsiDirectory

// Module, module group, package and content root nodes get their icons from the
// IDE rather than from IconProvider, so they are overridden here.
class ProjectViewDecorator : ProjectViewNodeDecorator {

  override fun decorate(node: ProjectViewNode<*>, data: PresentationData) {
    val icon = when (val value = node.value) {
      is Module -> IconResolver.forModule(value.name)
      is ModuleGroup -> Icons.folder
      is PsiDirectory -> IconResolver.forFile(value.virtualFile)
      else -> null
    }

    icon?.let(data::setIcon)
  }
}
