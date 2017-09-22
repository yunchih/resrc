# Maintainer: Yunchih Chen <yunchih@csie.ntu.edu.tw>
modulename=systemd-logind-hook
pkgname="python-${modulename}"
pkgver=1.1
pkgrel=1
pkgdesc="Systemd-logind resource hook"
arch=('any')
url="https://github.com/yunchih/systemd-logind-hook"
license=('MIT')
depends=('pacman' 'python>=3.3')
source=("https://github.com/yunchih/systemd-logind-hook/archive/${pkgver}.tar.gz")
md5sums=('ac1177c61a5836c964632577246a82fe')
package() {
  cd "${srcdir}/${modulename}-${pkgver}"
  python setup.py install --root="${pkgdir}" --optimize=1
  install -D -m644 examples/config.yaml "${pkgdir}/usr/share/${pkgname}/examples/config.yaml"
}
