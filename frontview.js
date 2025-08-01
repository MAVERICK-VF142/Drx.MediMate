function handleSymptomSubmit(symptom) {
  navigator.geolocation.getCurrentPosition((position) => {
    const userLocation = {
      lat: position.coords.latitude,
      lon: position.coords.longitude,
    };

    fetch('/api/mapSearch', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ symptom, location: userLocation }),
    })
      .then(res => res.json())
      .then(data => {
        setMedicineList(data.medicines);
        setDoctors(data.nearby_doctors);
        setMapCenter(userLocation);
      });
  });
}
