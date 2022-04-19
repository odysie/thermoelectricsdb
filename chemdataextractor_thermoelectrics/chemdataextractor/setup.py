import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ChemDataExtractor-TE",
    version="2.0.0-te",
    author='Matt Swain, Callum Court, Edward Beard, Juraj Mavracic, Taketomo Isazawa, adapted by Odysseas Sierepeklis',
    author_email='m.swain@me.com, cc889@cam.ac.uk, ejb207@cam.ac.uk, jm2111@cam.ac.uk, ti250@cam.ac.uk, os403@cam.ac.uk',
    license='MIT',
    description="ChemDataExtractor 2.0 adapted for the thermoelectric materials domain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages()
)