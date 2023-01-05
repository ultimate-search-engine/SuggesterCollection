import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.7.10"
}

group = "use.algorithm.exanys"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    maven("https://jitpack.io") {
        content {
            includeGroup("com.github.jillesvangurp.kt-search")
        }
    }
}

dependencies {
    testImplementation(kotlin("test"))
    implementation("com.github.jillesvangurp.kt-search:search-client:1.99.18")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "1.8"
}