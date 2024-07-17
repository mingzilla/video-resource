## Common Design Patterns
* Factory - use create method to create objects, instead of new keyword
* Singleton - prevent multiple instances of class
* Facade - protect code that uses 3rd party code
* Strategy - use composition to handle polymophism
* Observable - subscription rather than calling methods

## Factory

```groovy
class User { 
  String name
  String type

  private User() {} // prevent external creation

  static User createForStudent(String name) {
    return new User(name: name, type: 'student')
  }

  static User createForTeacher(String name) {
    return new User(name: name, type: 'teacher')
  }
}
```

## Singleton

```groovy
class UserService {
    private static UserService instance

    private UserService() {}

    public static UserService getInstance() {
        if (instance == null) instance = new UserService()
        return instance
    }
}
```

## Facade

```groovy
class MyUtil {
  public boolean isBlank(String text) {
    return StringUtils.isBlank(text) // apache StringUtils
  }
}
```

## Strategy

```groovy
interface Animal {
    void run()
}

class Dog implements Animal {
    void run() { println('Using 4 legs') }
}

class Bird implements Animal {
    void run() { println('Jump') }
}

class AnimalCosplayer {
    Animal animal
    AnimalCosplayer(Animal animal) { this.animal = animal }
    void run() { animal.run() }
}

new AnimalCosplayer(new Dog()).run() // Using 4 legs
new AnimalCosplayer(new Bird()).run() // Jump
```

## Observable

```ts
service.getNumObservable().subscribe((data) => {
    console.log(data);
}); // many places

service.numObservable.emit(1); // send 1 to many places
```