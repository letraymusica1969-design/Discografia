import './globals.css';
import Nav from '../components/Nav';
import Footer from '../components/Footer';
import AudioProvider from '../components/AudioProvider';
import GlobalPlayer from '../components/GlobalPlayer';

export const metadata = {
  title: 'Sandro Saavedra — Canciones de una Ciudad',
  description:
    'Sandro Saavedra · Box set de 6 discos en vinilo. Música y letra. Canciones de una ciudad — 78 temas.',
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