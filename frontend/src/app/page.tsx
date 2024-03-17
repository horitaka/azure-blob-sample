"use client";

import { useState } from "react";
import { BlockBlobClient } from "@azure/storage-blob";

export default function Home() {
  const [file, setFile] = useState<File>();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;

    const file = event.target.files[0];
    setFile(file);
  };

  const handleUpload = async () => {
    if (!file) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL as string;
    const response = await fetch(apiUrl, { method: "POST" });
    const url = (await response.json()).url;
    const client = new BlockBlobClient(url);
    await client.uploadData(file);
  };

  return (
    <div>
      <input type="file" onChange={handleFileSelect} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
