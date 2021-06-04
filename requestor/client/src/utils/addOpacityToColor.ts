export default (color: string, opacity: number) => {
  switch (opacity) {
    case 5:
      return color + '0d';
    case 10:
      return color + '1a';
    case 15:
      return color + '26';
    case 20:
      return color + '33';
    case 25:
      return color + '40';
    case 30:
      return color + '4d';
    case 35:
      return color + '59';
    case 45:
      return color + '73';
    case 50:
      return color + '80';
    case 70:
      return color + 'b3';
    case 80:
      return color + 'cc';
    case 95:
      return color + 'f2';
    default:
      return color;
  }
};
