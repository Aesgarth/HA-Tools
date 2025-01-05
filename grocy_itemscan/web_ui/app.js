document.getElementById("scanButton").addEventListener("click", () => {
  // Start the scanner
  Quagga.init({
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: document.querySelector("#preview"),
    },
    decoder: {
      readers: ["ean_reader"],
    },
  }, (err) => {
    if (err) {
      console.error(err);
      return;
    }
    console.log("Barcode scanner initialized.");
    Quagga.start();
  });

  // Detect barcodes
  Quagga.onDetected((data) => {
    console.log("Detected barcode:", data.codeResult.code);
    Quagga.stop();

    // Send to backend
    fetch("/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ barcode: data.codeResult.code }),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.error("Error:", error));
  });
});
