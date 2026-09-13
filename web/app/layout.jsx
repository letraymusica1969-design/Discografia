import './globals.css';
import Nav from '../components/Nav';
import Footer from '../components/Footer';
import AudioProvider from '../components/AudioProvider';
import GlobalPlayer from '../components/GlobalPlayer';

export const metadata = {
  title: 'San Cougar — Canciones de una Ciudad',
  description:
    'San Cougar · Box set de 6 discos en vinilo. Música y letra. Canciones de una ciudad — 80 temas.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <AudioProvider>
          <Nav />
          {children}
          <Footer />
          <GlobalPlayer />
        </AudioProvider>
      </body>
    </html>
  );
}