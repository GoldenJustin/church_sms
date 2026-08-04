# Church SMS - Frappe App

A simple SMS management app for church members, designed to work with the existing ChurchSMS DocTypes on KODA ERP.

## Features
- Send bulk SMS to all church members
- Send SMS to specific branches
- Send SMS to selected members
- Auto-formats phone numbers to Tanzania international format (255...)
- Integration with Africa's Talking SMS API

## Installation

```bash
bench get-app https://github.com/GoldenJustin/church_sms.git
bench --site kodaerp.benethemmanuel.site install-app church_sms
bench --site kodaerp.benethemmanuel.site migrate
bench restart
```

## Configuration

1. Go to **Church SMS Settings**
2. Set your API Key, API Secret, and Default Sender ID
3. Save

## Usage

1. Go to **Church SMS** > **New**
2. Select "Send To": All Members / Specific Branch / Specific Members
3. Write your message
4. Click "Send SMS"

## Existing DocTypes (already on site)
- Church SMS
- Church SMS Settings
- Church SMS Recipient
- Church Member
- Church Branch
