package com.github.sebastiandotdev.symbols

import com.intellij.testFramework.fixtures.BasePlatformTestCase
import com.intellij.psi.PsiManager

class MyPluginTest : BasePlatformTestCase() {
  
  private val provider = IconProvider()
  
  fun testUsesExactFileNameIconWhenAvailable() {
    val psiFile = myFixture.configureByText("tsconfig.json", "{}")
    
    val icon = provider.getIcon(psiFile, 0)
    
    assertSame(Icons.tsconfig, icon)
    assertNotSame(Icons.brackets_yellow, icon)
  }
  
  fun testMatchesMixedCaseFileNameFromTheme() {
    val psiFile = myFixture.configureByText("CLAUDE.md", "")

    val icon = provider.getIcon(psiFile, 0)

    assertSame(Icons.claude, icon)
    assertNotSame(Icons.markdown, icon)
  }

  fun testUsesSourceSetFolderIconForGradleModule() {
    assertSame(IconResolver.forFolder("test"), IconResolver.forModule("Symbols.test"))
  }

  fun testUsesDefaultFolderIconForUnknownModule() {
    assertSame(Icons.folder, IconResolver.forModule("Symbols"))
  }

  fun testUsesCompositeExtensionBeforeSimpleExtension() {
    val psiFile = myFixture.configureByText("feature.test.tsx", "export {}")
    
    val icon = provider.getIcon(psiFile, 0)
    
    assertSame(Icons.react_test, icon)
    assertNotSame(Icons.react_ts, icon)
    assertNotSame(Icons.ts, icon)
  }
  
  fun testUsesFolderSpecificIcon() {
    val dirVFile = myFixture.tempDirFixture.findOrCreateDir("assets")
    val directory = PsiManager.getInstance(project).findDirectory(dirVFile)
    
    assertNotNull(directory)
    val icon = provider.getIcon(directory!!, 0)
    
    assertSame(Icons.folder_assets, icon)
  }
  
  fun testUsesDefaultFolderIconWhenFolderIsUnknown() {
    val dirVFile = myFixture.tempDirFixture.findOrCreateDir("random-folder")
    val directory = PsiManager.getInstance(project).findDirectory(dirVFile)
    
    assertNotNull(directory)
    val icon = provider.getIcon(directory!!, 0)
    
    assertSame(Icons.folder, icon)
  }
  
  fun testReturnsNullForUnknownFileType() {
    val psiFile = myFixture.configureByText("something.unknownext", "data")
    
    val icon = provider.getIcon(psiFile, 0)
    
    assertNull(icon)
  }
}
