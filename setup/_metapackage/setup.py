import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-data-import",
    description="Meta package for open-synergy-ssi-data-import Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_data_import',
        'odoo14-addon-ssi_data_import_operating_unit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
