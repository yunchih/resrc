# Maintainer: Yunchih Chen <yunchih@csie.ntu.edu.tw>
modulename=resrc
pkgname="python-${modulename}"
pkgver=1.3
pkgdesc="A tool that limits total CGroup resources available to a user within all her sessions"
arch=('any')
url="https://github.com/yunchih/resrc"
license=('MIT')
depends=('pacman' 'python>=3.3' 'python-dbus' 'python-yaml' 'python-gobject')
source=("https://github.com/yunchih/resrc/releases/download/v${pkgver}/${modulename}-${pkgver}.tar.gz")
md5sums=('10f515c3b67858b1c2a617105fb9898d')
package() {
  cd "${srcdir}/${modulename}-${pkgver}"
  python setup.py install --root="${pkgdir}" --optimize=1
  install -D -m644 examples/config.yaml "${pkgdir}/usr/share/${pkgname}/examples/config.yaml"
}
