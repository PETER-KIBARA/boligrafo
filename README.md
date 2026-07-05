# Post-diagnosis Hypertension management system

Boligrafo is a health management app for blood pressure monitoring and hypertension care.

It combines a Flutter mobile app with a Django backend so patients and doctors can work in one system.

## Purpose

The project is designed to help with:

- tracking blood pressure readings
- managing patient and doctor profiles
- creating and reviewing prescriptions
- scheduling appointments
- sending notifications and reminders
- keeping care information organized in one place

## How it works

1. A patient signs in and adds vital readings.
2. The backend stores the data and links it to the correct profile.
3. A doctor reviews the patient’s information.
4. Prescriptions, treatments, and appointments are recorded.
5. Notifications help remind users about important follow-up actions.

## Main parts of the project

- frontend: Flutter app in boligrafo/lib
- backend: Django API in backend/postd
- database models: patients, doctors, vitals, prescriptions, treatments, notifications, and appointments

## Who it is for

- patients who need regular blood pressure follow-up
- doctors who monitor patients remotely
- clinics that want a simple digital workflow for hypertension care

## In short

Boligrafo is a simple care platform built to make hypertension monitoring easier for both patients and doctors.
