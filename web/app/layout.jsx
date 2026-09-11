import './globals.css';
import Nav from '../components/Nav';
import Footer from '../components/Footer';

export const metadata = {
  title: 'Sandro Saavedra — Canciones de una Ciudad',
  description:
    'Sandro Saavedra · Box set de 6 discos en vinilo. Música y letra. Canciones de una ciudad — 79 temas.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <Nav />
        {children}
        <Footer />
      </body>
    </html>
  );
}