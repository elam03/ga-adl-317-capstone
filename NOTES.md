### Other

One-Hot Encoding (specifically its Multi-Hot variant) performs the following key functions:

Numerical Conversion: It converts the text-based lists of board game categories and mechanics (like ['Economic', 'Fantasy']) into a format of 1s and 0s that the neural network can use for mathematical calculations.
Multi-Label Representation: Since a single game can have multiple mechanics and categories simultaneously, the encoding creates a long binary vector where multiple positions can be '1' at the same time to represent the full profile of the game.
Feature Mapping: It maps each unique attribute to a specific input neuron in the BaselineNet. This allows the model to learn weights for individual features—for example, it can learn if the presence of 'Dice Rolling' typically correlates with a specific rating range.
Dimensionality Management: By using a fixed vocabulary of categories and mechanics, it creates a structured input space (approximately 280 features) that is much easier for a simple neural network to process than raw text descriptions or high-cardinality data like designer names.
