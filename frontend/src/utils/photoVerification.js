// Simulates backend GPS/perceptual-hash verification for demo purposes.
// Randomly assigns a realistic outcome so the upload flow feels real.
export function simulatePhotoVerification() {
  const outcomes = [
    { status: "verified", distanceM: Math.floor(Math.random() * 15) + 2 },
    { status: "location_mismatch", distanceM: Math.floor(Math.random() * 300) + 100 },
    { status: "no_gps_data", distanceM: null },
  ];
  const rand = Math.random();
  if (rand < 0.7) return outcomes[0];
  if (rand < 0.9) return outcomes[1];
  return outcomes[2];
}