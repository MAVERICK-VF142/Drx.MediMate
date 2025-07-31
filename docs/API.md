# 🔗 Drx.MediMate API Documentation

This document provides comprehensive information about the Drx.MediMate API endpoints.

## 📋 Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)

## 🔐 Authentication

Currently, the API uses Firebase Authentication for user management. Users must be authenticated to access most endpoints.

## 🌐 Base URL

```
Production: https://your-domain.com
Development: http://127.0.0.1:5000
```

## ⚠️ Error Handling

All API responses follow a consistent error format:

### Success Response
```json
{
  "response": "Detailed information about the drug...",
  "status": 200
}
```

### Error Response
```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400,
  "timestamp": 1640995200,
  "error_id": "12345" // For internal errors
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable - AI service down |

## 🚦 Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Default Limit**: 60 requests per minute per IP
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns 429 status with retry information

## 📚 Endpoints

### 1. Drug Information

Get detailed clinical information about a specific drug.

**Endpoint**: `POST /get_drug_info`

**Request Body**:
```json
{
  "drug_name": "aspirin"
}
```

**Response**:
```json
{
  "response": "## Therapeutic Uses\n- Pain relief\n- Anti-inflammatory\n\n## Standard Dosage\n- Adult: 325-650mg every 4 hours\n\n## Common Side Effects\n- Stomach upset\n- Nausea\n\n## Serious Side Effects\n- Gastrointestinal bleeding\n- Allergic reactions\n\n## Contraindications\n- Allergy to salicylates\n- Active bleeding\n\n## Important Drug Interactions\n- Warfarin (increased bleeding risk)\n- Methotrexate (increased toxicity)"
}
```

**Errors**:
- `400`: Missing drug_name
- `503`: AI service unavailable

---

### 2. Symptom Checker

Get treatment recommendations based on symptoms.

**Endpoint**: `POST /symptom_checker`

**Request Body**:
```json
{
  "symptoms": "headache, fever, body aches"
}
```

**Response**:
```json
{
  "response": "## Recommended Over-the-Counter Treatments\n- Acetaminophen 500mg every 6 hours\n- Ibuprofen 200mg every 6-8 hours\n- Rest and hydration\n\n## Common Side Effects\n- Acetaminophen: Rare at recommended doses\n- Ibuprofen: Stomach upset, dizziness\n\n## Important Interactions\n- Avoid alcohol with acetaminophen\n- Ibuprofen may interact with blood thinners\n\n## Safety Tips\n- Do not exceed recommended doses\n- **Seek immediate medical attention if symptoms worsen or persist beyond 3 days**"
}
```

**Errors**:
- `400`: Missing symptoms
- `503`: AI service unavailable

---

### 3. Image Analysis

Analyze medicine packaging from uploaded images.

**Endpoint**: `POST /process-upload`

**Request Body** (Form Data):
```
image_data: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
```

**Response**:
```json
{
  "result": "## Drug Information\n- **Drug Name**: Aspirin 325mg\n- **Manufacturer**: Bayer\n\n## Clinical Summary\n- **Therapeutic Uses**: Pain relief, fever reduction\n- **Standard Dosage**: 1-2 tablets every 4 hours\n- **Common Side Effects**: Stomach upset, nausea\n- **Serious Side Effects**: GI bleeding, allergic reactions\n- **Contraindications**: Active bleeding, salicylate allergy\n- **Important Interactions**: Warfarin, alcohol"
}
```

**Errors**:
- `400`: Invalid image format
- `400`: No image data received
- `503`: AI service unavailable

---

### 4. Prescription Validation

Validate prescription images and check for potential issues.

**Endpoint**: `POST /validate-prescription`

**Request Body** (Form Data):
```
image_data: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
```

**Response**:
```json
{
  "result": "## Extracted Prescription\n- Drug 1: Lisinopril, 10mg, Once daily, 30 days\n- Drug 2: Metformin, 500mg, Twice daily, 30 days\n\n## AI-Powered Feedback\n- Safety Warnings: None detected\n- Interaction Notes: No significant interactions found\n- Suggestions: Monitor blood pressure and blood glucose levels regularly"
}
```

**Errors**:
- `400`: Invalid image format
- `400`: No image data received
- `503`: AI service unavailable

---

### 5. Allergy Checker

Check medicines against known allergies.

**Endpoint**: `POST /allergy_checker`

**Request Body**:
```json
{
  "allergies": "penicillin, sulfa drugs",
  "medicines": "amoxicillin, sulfamethoxazole, acetaminophen"
}
```

**Response**:
```json
{
  "response": "## Allergy Analysis Results\n\n### ⚠️ **DANGEROUS COMBINATIONS DETECTED**\n\n- **Amoxicillin**: ❌ **NOT SAFE** - This is a penicillin-based antibiotic\n  - **Risk**: Severe allergic reaction possible\n  - **Recommendation**: Do not take this medication\n\n- **Sulfamethoxazole**: ❌ **NOT SAFE** - Contains sulfa compounds\n  - **Risk**: Allergic reaction due to sulfa allergy\n  - **Recommendation**: Avoid this medication\n\n- **Acetaminophen**: ✅ **SAFE** - No known interaction with your allergies\n  - **Note**: Can be used as directed\n\n### 🚨 **IMPORTANT**: Consult your healthcare provider immediately before taking any new medications."
}
```

**Errors**:
- `400`: Missing allergies
- `400`: Missing medicines
- `503`: AI service unavailable

---

## 🔧 Development Usage

### Using cURL

```bash
# Drug Information
curl -X POST http://127.0.0.1:5000/get_drug_info \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "aspirin"}'

# Symptom Checker
curl -X POST http://127.0.0.1:5000/symptom_checker \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "headache, fever"}'

# Allergy Checker
curl -X POST http://127.0.0.1:5000/allergy_checker \
  -H "Content-Type: application/json" \
  -d '{"allergies": "penicillin", "medicines": "amoxicillin"}'
```

### Using Python Requests

```python
import requests

# Drug Information
response = requests.post('http://127.0.0.1:5000/get_drug_info', 
                        json={'drug_name': 'aspirin'})
print(response.json())

# Symptom Checker
response = requests.post('http://127.0.0.1:5000/symptom_checker',
                        json={'symptoms': 'headache, fever'})
print(response.json())
```

## 📝 Notes

1. **AI Responses**: All AI-generated content is formatted in Markdown for better readability
2. **Caching**: Drug information responses are cached for 10 minutes to improve performance
3. **Timeouts**: AI requests have a 10-second timeout with 3 retry attempts
4. **Educational Use**: This system is designed for educational purposes and should not replace professional medical advice

## 🤝 Contributing

To contribute to the API documentation:

1. Update this file with new endpoints
2. Include example requests and responses
3. Document error cases
4. Test all examples before submitting

---

*Last updated: January 2025*
