# Maintainer: Yunchih Chen <yunchih@csie.ntu.edu.tw>
modulename=resrc
pkgname="python-${modulename}"
pkgver=1.1
pkgrel=1
pkgdesc="Systemd-logind resource hook"
arch=('any')
url="https://github.com/yunchih/systemd-logind-hook"
license=('MIT')
depends=('pacman' 'python>=3.3')
source=("https://github.com/yunchih/systemd-logind-hook/archive/v${pkgver}.tar.gz")
md5sums=('6f324bfe619b5177d00aea3d676a6773')
package() {
  cd "${srcdir}/${modulename}-${pkgver}"
  python setup.py install --root="${pkgdir}" --optimize=1
  install -D -m644 examples/config.yaml "${pkgdir}/usr/share/${pkgname}/examples/config.yaml"
}
