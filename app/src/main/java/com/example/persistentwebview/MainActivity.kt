package com.example.persistentwebview

import android.content.Context
import android.os.Bundle
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    private val loginUrl = "https://grpmb.sehan.ac.kr/mobile/#/login"
    private val cookiePrefsName = "webview_cookie_store"
    private val cookieKey = "sehan_cookie"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        configureCookiePolicy()
        configureWebView()

        if (savedInstanceState == null) {
            restoreCookies(loginUrl)
            webView.loadUrl(loginUrl)
        } else {
            webView.restoreState(savedInstanceState)
        }

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    private fun configureCookiePolicy() {
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        cookieManager.setAcceptThirdPartyCookies(webView, true)
    }

    private fun configureWebView() {
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                return false
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                saveCookies(loginUrl)
            }
        }

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            databaseEnabled = true
            loadsImagesAutomatically = true
            mixedContentMode = WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE
        }
    }

    private fun saveCookies(url: String) {
        val cookie = CookieManager.getInstance().getCookie(url) ?: return
        getSharedPreferences(cookiePrefsName, Context.MODE_PRIVATE)
            .edit()
            .putString(cookieKey, cookie)
            .apply()

        CookieManager.getInstance().flush()
    }

    private fun restoreCookies(url: String) {
        val savedCookie = getSharedPreferences(cookiePrefsName, Context.MODE_PRIVATE)
            .getString(cookieKey, null)
            ?: return

        val cookieManager = CookieManager.getInstance()
        savedCookie.split(";")
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .forEach { cookiePart ->
                cookieManager.setCookie(url, cookiePart)
            }
        cookieManager.flush()
    }

    override fun onPause() {
        super.onPause()
        saveCookies(loginUrl)
        webView.onPause()
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
