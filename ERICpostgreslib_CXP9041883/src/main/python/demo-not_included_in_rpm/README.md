# Demo Folder

## Not to be included in the RPM Build

If you are including a new Python package that is required to be added to
the build, please be specific with the package name in the pom file.

### For example:

```
<mapping>
  <directory>/${rpm-root}/${comp-name}/${install-path}/<<new package>></directory>
  <filemode>755</filemode>
  <username>root</username>
  <groupname>root</groupname>
  <configuration>false</configuration>
  <directoryIncluded>true</directoryIncluded>
  <recurseDirectories>true</recurseDirectories>
  <sources>
    <source>
    <location>src/main/python/<<new package>></location>
    <excludes>
      <exclude>**/*.pyc</exclude>
      <exclude>**/*.pyo</exclude>
    </excludes>
    </source>
  </sources>
</mapping>
```

*And same for pycode style and nose tests.*

