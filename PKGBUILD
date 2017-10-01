# Maintainer: Yunchih Chen <yunchih@csie.ntu.edu.tw>
modulename=resrc
pkgname="python-${modulename}"
pkgver=1.2
pkgdesc="Systemd-logind resource hook"
arch=('any')
url="https://github.com/yunchih/systemd-logind-hook"
license=('MIT')
depends=('pacman' 'python>=3.3' 'python-dbus' 'python-yaml')
source=("https://github.com/yunchih/resrc/releases/download/v${pkgver}/${modulename}-${pkgver}.tar.gz")
md5sums=('2e3849e05d54cd7e72726ac807a65067')
package() {
  cd "${srcdir}/${modulename}-${pkgver}"
  python setup.py install --root="${pkgdir}" --optimize=1
  install -D -m644 examples/config.yaml "${pkgdir}/usr/share/${pkgname}/examples/config.yaml"
}
